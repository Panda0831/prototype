import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import time

from src.blockchain.transaction import Transaction, SecteurActivite
from src.algorithms.astar import AStar
from src.models.graph import DistrictsGraph

class AgriculturalLot(BaseModel):
    id: str
    owner_id: str
    product_type: str  # ex: Vanille, Girofle, Litchi, Riz
    district_origin: str
    weight: float  # en kg
    quality: str  # ex: Premium, Standard, Grade A
    status: str  # RECOLTE, COLLECTE, EN_TRANSIT, EXPORTE, CERTIFIE_CONFORME
    traceability: List[dict] = []
    ai_inspection: Optional[Dict[str, Any]] = None
    passport_hash: Optional[str] = None

class AgricultureManager:
    """
    Gère le cycle de vie des produits agricoles malgaches.
    Récolte -> Transport Optimisé (A*) -> Blockchain.
    """
    def __init__(self, blockchain, districts_graph: DistrictsGraph):
        self.blockchain = blockchain
        self.graph = districts_graph
        self.astar = AStar(districts_graph)
        self.lots: Dict[str, AgriculturalLot] = {}

    def register_harvest(
        self,
        owner_id: str,
        product_type: str,
        district: str,
        weight: float,
        quality: str,
        ai_inspection: Optional[Dict[str, Any]] = None
    ):
        """Enregistre une nouvelle récolte sur la blockchain."""
        # ID simplifié : HZL-TIMESTAMP
        lot_id = f"HZL-{int(time.time())}"
        passport_hash = ai_inspection.get("inspection_hash") if ai_inspection else None
        
        lot = AgriculturalLot(
            id=lot_id,
            owner_id=str(owner_id),
            product_type=product_type,
            district_origin=district,
            weight=weight,
            quality=quality,
            status="CERTIFIE_CONFORME" if (ai_inspection and ai_inspection.get("status") == "APPROVED_FOR_BLOCKCHAIN") else "RECOLTE",
            traceability=[{
                "action": "CERTIFICATION_IA_RECOLTE" if ai_inspection else "RECOLTE",
                "lieu": district,
                "timestamp": time.time(),
                "details": ai_inspection
            }],
            ai_inspection=ai_inspection,
            passport_hash=passport_hash
        )
        
        # Inscription Blockchain
        dest = "COOPERATIVE_REGIONALE_SAVA" if "vanille" in product_type.lower() else "COOPERATIVE_REGIONALE"
        desc = f"Passeport Numérique Vanille {lot_id} ({quality}) à {district}" if ai_inspection else f"Récolte de {weight}kg de {product_type} ({quality}) à {district}"
        
        tx = Transaction(
            expediteur=owner_id,
            destinataire=dest,
            donnees=lot.dict(),
            secteur=SecteurActivite.PRODUITS_AGRICOLES,
            description=desc,
            montant=0
        )
        tx.signature = "SIG_PROD_DEMO"
        
        if self.blockchain.ajouter_transaction(tx):
            self.lots[lot_id] = lot
            print(f"DEBUG: Transaction for lot {lot_id} added to mempool.")
            return lot
        return None

    def sell_lot(self, lot_id: str, buyer_id: str, price: float, seller_id: str):
        """
        Enregistre la vente d'un lot sur la blockchain (transfert d'ownership).
        Vérifie que le vendeur est bien le propriétaire actuel.
        """
        lot = self.lots.get(lot_id)
        if not lot:
            return None
        
        # Vérification de propriété
        def normalize(k): return re.sub(r'[^a-zA-Z0-9]', '', str(k)).lower()
        if normalize(lot.owner_id) != normalize(seller_id):
            print(f" [!] FRAUDE DÉTECTÉE : {seller_id} tente de vendre un lot appartenant à {lot.owner_id}")
            return None
        
        # Transaction Blockchain pour le transfert de propriété
        tx = Transaction(
            expediteur=lot.owner_id,
            destinataire=buyer_id,
            donnees={"lot_id": lot_id, "action": "SALE", "price": price},
            secteur=SecteurActivite.PRODUITS_AGRICOLES,
            description=f"Vente du lot {lot_id} ({lot.product_type})",
            montant=0
        )
        tx.signature = "SIG_VENDEUR_DEMO"
        
        if self.blockchain.ajouter_transaction(tx):
            # Mise à jour différée via minage
            print(f"DEBUG: Sale transaction for lot {lot_id} added to mempool.")
            return lot
        return None

    def optimize_transport(self, lot_id: str, destination_district: str):
        """Calcule le chemin optimal entre deux districts pour n'importe quel produit."""
        
        # Recherche sécurisée du lot
        lot = next((v for k, v in self.lots.items() if k == lot_id), None)
        
        if lot is None:
            print(f"DEBUG: Lot not found with ID {lot_id}. Available keys: {list(self.lots.keys())}")
            return None
            
        print(f"DEBUG: Found lot: {lot.id}, origin: {lot.district_origin}, destination: {destination_district}")
        
        start_node = next((d for d in self.graph.districts.values() if d.nom.strip().lower() == lot.district_origin.strip().lower()), None)
        end_node = next((d for d in self.graph.districts.values() if d.nom.strip().lower() == destination_district.strip().lower()), None)
        
        if not start_node or not end_node:
            print(f"DEBUG: Could not find start node '{lot.district_origin}' or end node '{destination_district}'")
            return None
            
        path_ids, distance = self.astar.chercher(start_node.id, end_node.id)
        if not path_ids:
            print(f"DEBUG: A* found no path")
            return None

        path_names = [self.graph.districts[node_id].nom for node_id in path_ids]
        
        # Transaction Blockchain
        tx = Transaction(
            expediteur=lot.owner_id,
            destinataire=f"CENTRE_COLLECTE_{destination_district.upper()}",
            donnees={"lot_id": lot_id, "chemin": path_names, "action": "TRANSPORT"},
            secteur=SecteurActivite.PRODUITS_AGRICOLES,
            description=f"Lot {lot_id} ({lot.product_type}) en transit vers {destination_district}",
            montant=0
        )
        tx.signature = "SIG_COLLECTEUR_DEMO"
        self.blockchain.ajouter_transaction(tx)
        
        print(f"DEBUG: Transport transaction for lot {lot_id} added to mempool.")
        return lot, path_names
