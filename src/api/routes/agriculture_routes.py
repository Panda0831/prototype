import base64
import binascii
import hashlib
import time
from typing import List, Optional

from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from src.ai.market_model import vanilla_market
from src.ai.vanilla_ai import vanilla_ai
from src.ai.vision import get_vision_model
from src.algorithms.astar import AStar
from src.api.deps import get_current_user
from src.api.instances import (
    agriculture_manager,
    blockchain_instance,
    foncier_uf,
    graphe,
    microfinance_manager,
    notifications,
    pending_diploma_requests,
    pending_land_requests,
    pending_transfers,
    all_instances,
)
from src.db.models import User
from src.use_cases.produitsAgricoles import AgriculturalLot
from src.utils.persistence import save_state
from src.utils.sync import synchronize_state

router = APIRouter()


class HarvestRequest(BaseModel):
    owner_id: str
    product_type: str
    district: str
    weight: float
    quality: str


class VanillaInspectionRequest(BaseModel):
    district: str = "Sambava"
    bean_length_cm: float = 18.0
    moisture_pct: float = 32.0
    vanillin_pct: float = 2.2
    mold_detected: bool = False
    maturity_pct: float = 96.0
    image_base64: Optional[str] = None


class VanillaSealRequest(BaseModel):
    owner_id: str
    district: str = "Sambava"
    weight: float = 5.0
    bean_length_cm: float = 18.0
    moisture_pct: float = 32.0
    vanillin_pct: float = 2.2
    mold_detected: bool = False
    maturity_pct: float = 96.0
    image_base64: Optional[str] = None


MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _decode_photo(image_base64: Optional[str]) -> Optional[bytes]:
    """Décode la photo bord-champ (data URL ou base64 brut) destinée au passeport."""
    if not image_base64:
        return None
    payload = image_base64.split(",", 1)[1] if image_base64.startswith("data:") else image_base64
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Photo illisible (base64 invalide)")
    if not raw:
        raise HTTPException(status_code=400, detail="Photo vide")
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Photo trop volumineuse (max 5 Mo)")
    return raw


class TransportRequest(BaseModel):
    lot_id: str
    destination: str


class SellRequest(BaseModel):
    lot_id: str
    buyer_id: str
    price: float
    seller_id: str  # Clé publique du vendeur


@router.post("/harvest")
async def record_harvest(data: HarvestRequest):
    """Enregistre une nouvelle récolte sur la blockchain."""
    lot = agriculture_manager.register_harvest(
        data.owner_id, data.product_type, data.district, data.weight, data.quality
    )
    if not lot:
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement")

    save_state(
        blockchain_instance,
        foncier_uf,
        pending_land_requests,
        agriculture_manager.lots,
        pending_diploma_requests,
        microfinance_manager.pending_transfers,
    )
    return {"status": "SUCCESS", "lot": lot}


@router.post("/transport")
async def optimize_transport(request: Request, data: TransportRequest):
    """Optimise le trajet de transport pour un lot."""
    result = agriculture_manager.optimize_transport(data.lot_id, data.destination)
    if not result:
        raise HTTPException(
            status_code=404, detail="Lot non trouvé ou erreur de routage"
        )

    lot, path = result

    save_state(
        blockchain_instance,
        foncier_uf,
        pending_land_requests,
        agriculture_manager.lots,
        pending_diploma_requests,
        microfinance_manager.pending_transfers,
    )
    return {"status": "SUCCESS", "lot": lot, "path": path}


@router.post("/sell")
async def sell_lot(data: SellRequest, current_user: User = Depends(get_current_user)):
    """Enregistre une offre de vente d'un lot."""
    # 1. Vérification de propriété
    lot_actuel = agriculture_manager.lots.get(data.lot_id)
    if not lot_actuel or lot_actuel.owner_id != current_user.public_key:
        raise HTTPException(
            status_code=403, detail="Action interdite : Vous ne possédez pas ce lot."
        )

    # 2. Créer une offre de vente (notification)
    sale_offer_id = f"SALE-{int(time.time())}"
    notifications.append(
        {
            "public_key": data.buyer_id,
            "message": f"🛍️ Offre d'achat de {lot_actuel.product_type} pour {data.price} MGA.",
            "sale_offer_id": sale_offer_id,
            "lot_id": data.lot_id,
            "seller_id": current_user.public_key,
            "price": data.price,
            "timestamp": time.time(),
        }
    )

    return {"status": "SUCCESS", "message": "Offre envoyée à l'acheteur"}


@router.post("/accept-sale/{sale_offer_id}")
async def accept_sale(
    sale_offer_id: str, current_user: User = Depends(get_current_user)
):
    """L'acheteur accepte l'offre, créant le transfert financier."""
    print(f" [DEBUG] Accept Sale: User {current_user.public_key}, Offer {sale_offer_id}")
    
    # Debug: Check offers
    for n in notifications:
        print(f" [DEBUG] Checking notification: OfferID {n.get('sale_offer_id')}, UserKey {n.get('public_key')}")

    offer = next(
        (
            n
            for n in notifications
            if n.get("sale_offer_id") == sale_offer_id
            and str(n["public_key"]) == str(current_user.public_key)
        ),
        None,
    )

    if not offer:
        # Check if the offer exists at all
        exists = any(n.get("sale_offer_id") == sale_offer_id for n in notifications)
        if exists:
             raise HTTPException(status_code=403, detail="Vous n'êtes pas le destinataire de cette offre.")
        raise HTTPException(status_code=404, detail="Offre non trouvée")

    # 1. Initier le paiement via Microfinance
    print(f" [DEBUG] Initiating transfer: Buyer {current_user.public_key}, Seller {offer['seller_id']}, Amount {offer['price']}")
    transfer = microfinance_manager.create_transfer_request(
        sender_id=current_user.public_key,
        receiver_id=offer["seller_id"],
        amount=offer["price"],
        description=f"Paiement Lot {offer['lot_id']}",
    )

    if not transfer:
        # Debug: Check balance
        bal = blockchain_instance.obtenir_solde(current_user.public_key)
        print(f" [DEBUG] Transfer failed! Buyer balance: {bal}, Amount: {offer['price']}")
        raise HTTPException(
            status_code=400, detail=f"Solde insuffisant. Vous avez {bal} MGA, besoin de {offer['price']} MGA."
        )

    # Automatiquement accepter le transfert pour finaliser la vente
    _, error = microfinance_manager.accept_transfer(transfer["id"])
    if error:
        raise HTTPException(
            status_code=400, detail=f"Échec du transfert financier : {error}"
        )

    # 2. Transférer le lot (sera miné dans la blockchain)
    lot = agriculture_manager.sell_lot(
        offer["lot_id"], current_user.public_key, offer["price"], offer["seller_id"]
    )

    # 3. Supprimer la notification
    notifications.remove(offer)

    save_state(
        blockchain_instance,
        foncier_uf,
        pending_land_requests,
        agriculture_manager.lots,
        pending_diploma_requests,
        microfinance_manager.pending_transfers,
    )
    return {"status": "SUCCESS", "message": "Vente acceptée, transfert initié"}


@router.get("/lot/{lot_id}")
async def get_lot_details(lot_id: str):
    """Consulte la traçabilité complète d'un produit."""
    if lot_id not in agriculture_manager.lots:
        raise HTTPException(status_code=404, detail="Lot non trouvé")
    return agriculture_manager.lots[lot_id]


@router.get("/all")
async def get_all_lots():
    """Liste tous les produits enregistrés."""
    return list(agriculture_manager.lots.values())


@router.post("/vanilla/inspect")
async def inspect_vanilla_lot(data: VanillaInspectionRequest):
    """Analyse IA prédictive pour un lot de vanille (ISO 5565-1 + k-NN Pricing)."""
    photo = _decode_photo(data.image_base64)
    inspection = vanilla_ai.inspect_lot(
        district=data.district,
        bean_length_cm=data.bean_length_cm,
        moisture_pct=data.moisture_pct,
        vanillin_pct=data.vanillin_pct,
        mold_detected=data.mold_detected,
        maturity_pct=data.maturity_pct,
        image_bytes=photo,
    )
    inspection["image_sha256"] = hashlib.sha256(photo).hexdigest() if photo else None
    inspection["image_attached"] = photo is not None
    return {"status": "SUCCESS", "inspection": inspection}


@router.get("/vanilla/model-info")
async def get_vanilla_model_info():
    """Métriques du modèle de pricing entraîné localement (MAE, RMSE, R², MAPE)."""
    return {"status": "SUCCESS", "model": vanilla_ai.pricing_model.summary()}


@router.get("/vanilla/market-info")
async def get_vanilla_market_info():
    """Série réelle UN Comtrade et modèle de marché entraîné localement."""
    return {"status": "SUCCESS", "market": vanilla_market.summary()}


@router.get("/vanilla/vision-info")
async def get_vanilla_vision_info():
    """Métriques du modèle de vision par ordinateur entraîné localement (Accuracy, MAE)."""
    return {"status": "SUCCESS", "vision": get_vision_model().summary()}


@router.post("/vanilla/seal")
async def seal_vanilla_passport(data: VanillaSealRequest):
    """Scelle immédiatement le diagnostic IA sur la blockchain sous forme de passeport numérique."""
    photo = _decode_photo(data.image_base64)
    inspection = vanilla_ai.inspect_lot(
        district=data.district,
        bean_length_cm=data.bean_length_cm,
        moisture_pct=data.moisture_pct,
        vanillin_pct=data.vanillin_pct,
        mold_detected=data.mold_detected,
        maturity_pct=data.maturity_pct,
        image_bytes=photo,
    )
    inspection["image_sha256"] = hashlib.sha256(photo).hexdigest() if photo else None
    inspection["image_attached"] = photo is not None

    lot = agriculture_manager.register_harvest(
        owner_id=data.owner_id,
        product_type="Vanille Bourbon (Madagascar)",
        district=data.district,
        weight=data.weight,
        quality=inspection["quality_grade"],
        ai_inspection=inspection
    )
    if not lot:
        raise HTTPException(status_code=500, detail="Échec de l'enregistrement du passeport en blockchain")

    # Auto-minage immédiat pour certifier le passeport dans un bloc décentralisé
    block = blockchain_instance.miner_transactions_en_attente("VALIDATEUR_SAVA_VANILLE")
    if block:
        synchronize_state(block, all_instances)

    save_state(
        blockchain_instance,
        foncier_uf,
        pending_land_requests,
        agriculture_manager.lots,
        pending_diploma_requests,
        microfinance_manager.pending_transfers,
    )

    tx_hash = block.transactions[-1].calculer_hash() if (block and block.transactions) else lot.passport_hash

    return {
        "status": "SUCCESS",
        "lot": lot,
        "inspection": inspection,
        "passport_hash": lot.passport_hash,
        "block_index": block.index if block else None,
        "block_hash": block.hash if block else None,
        "transaction_hash": tx_hash
    }


@router.get("/vanilla/dashboard-data")
async def get_vanilla_dashboard_data():
    """Données Data Science consolidées, agrégées depuis le dataset réel des 1000 lots."""
    data = vanilla_ai.data
    grade_counts = Counter(row["quality_grade"] for row in data)

    def mean(values):
        values = list(values)
        return sum(values) / len(values) if values else 0.0

    # Volumes et prix moyens par région (colonnes `region` réelles du dataset)
    regional_volumes = []
    for region in ("SAVA", "Analanjirofo", "Diana"):
        rows = [r for r in data if r["region"] == region]
        regional_volumes.append({
            "region": region,
            "volume": len(rows),
            "avg_price_mga": round(mean(r["fair_farmgate_price_mga"] for r in rows), -2),
        })

    # Courbe bord-champ : moyenne des prix sur 10 tranches de 100 lots consécutifs
    ordered = sorted(data, key=lambda r: r["lot_id"])
    bucket_size = max(1, len(ordered) // 10)
    price_trends = []
    for start in range(0, len(ordered), bucket_size):
        chunk = ordered[start:start + bucket_size]
        if not chunk:
            continue
        price_trends.append({
            "label": f"Lots {start + 1}-{start + len(chunk)}",
            "price": round(mean(r["fair_farmgate_price_mga"] for r in chunk), -2),
        })
    price_trends = price_trends[:10]

    gourmet = [r for r in data if r["quality_grade"] == "Gourmet_Grade_A"]

    d_sambava = next((d for d in graphe.districts.values() if "sambava" in d.nom.lower()), None)
    d_toamasina = next((d for d in graphe.districts.values() if "toamasina" in d.nom.lower()), None)

    path_names = []
    dist_km = 0.0
    if d_sambava and d_toamasina:
        astar = AStar(graphe)
        path_ids, dist_km = astar.chercher(d_sambava.id, d_toamasina.id)
        path_names = [graphe.districts[pid].nom for pid in path_ids]

    top_block = blockchain_instance.chaine[-1] if blockchain_instance.chaine else None
    latest_tx = top_block.transactions[-1] if (top_block and top_block.transactions) else None

    return {
        "price_trends": price_trends,
        "price_trends_source": f"Prix bord-champ réels, moyenne par tranche de {bucket_size} lots",
        "regional_volumes": regional_volumes,
        "quality_distribution": {
            "Gourmet_Grade_A": grade_counts.get("Gourmet_Grade_A", 0),
            "Standard_TK_Grade_B": grade_counts.get("Standard_TK_Grade_B", 0),
            "Extraction_Grade_C": grade_counts.get("Extraction_Grade_C", 0),
            "Rejected_Immature": grade_counts.get("Rejected_Immature", 0),
            "Defective_Mold": grade_counts.get("Defective_Mold", 0),
        },
        "metrics": {
            "high_price_mga": round(mean(r["fair_farmgate_price_mga"] for r in gourmet), -2),
            "fob_export_usd": round(mean(r["fob_export_price_usd"] for r in gourmet), 1),
            "target_maturity": 96.0,
            "iso_compliance": "ISO 5565-1 Compliant",
            "total_lots": len(agriculture_manager.lots),
            "dataset_lots": len(data),
        },
        "transport_routing": {
            "origin": "Sambava (SAVA)",
            "destination": "Port de Toamasina",
            "path": path_names,
            "distance_km": round(dist_km, 1),
            "efficiency": "Optimal (A*)",
        },
        "ai_model": vanilla_ai.pricing_model.summary(),
        "market": vanilla_market.summary(),
        "vision_model": get_vision_model().summary(),
        "dynamic_blockchain": {
            "transaction_hash": latest_tx.calculer_hash() if latest_tx else None,
            "block_index": top_block.index if top_block else None,
            "block_hash": top_block.hash if top_block else None,
            "confirmation_status": "Confirmed" if top_block else "Genesis",
            "validator": "VALIDATEUR_SAVA_VANILLE" if top_block else None,
        },
    }


@router.get("/vanilla/passport/{passport_hash}")
async def verify_vanilla_passport(passport_hash: str):
    """Vérification publique d'un passeport numérique (exportateur / contrôleur, sans compte)."""
    lot = next(
        (l for l in agriculture_manager.lots.values() if l.passport_hash == passport_hash),
        None,
    )
    if not lot:
        raise HTTPException(status_code=404, detail="Passeport inconnu")

    def _carries_passport(tx) -> bool:
        if isinstance(tx.donnees, dict):
            return tx.donnees.get("passport_hash") == passport_hash
        return hashlib.sha256(str(tx.donnees).encode()).hexdigest() == passport_hash

    block = next(
        (b for b in blockchain_instance.chaine if any(_carries_passport(t) for t in b.transactions)),
        None,
    )
    return {
        "status": "SUCCESS",
        "passport_hash": passport_hash,
        "authentic": True,
        "lot": lot,
        "certified_in_block": block.index if block else None,
    }
