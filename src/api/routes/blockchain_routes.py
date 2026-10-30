from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.api.instances import (
    blockchain_instance, foncier_uf, pending_land_requests, agriculture_manager, 
    diploma_manager, pending_diploma_requests, microfinance_manager, brain
)
from src.utils.persistence import save_state
from src.utils.sync import synchronize_state
from src.utils.crypto import Crypto
from src.blockchain.transaction import Transaction, SecteurActivite as BTSecteur
from src.api.schemas.blockchain import BlockchainSummary, BlockResponse, TransactionCreate, TransactionResponse

router = APIRouter()

@router.get("/", response_model=BlockchainSummary)
async def get_blockchain_status():
    """Retourne un résumé de l'état de la blockchain."""
    return {
        "longueur": len(blockchain_instance.chaine),
        "dernier_hash": blockchain_instance.obtenir_dernier_bloc().hash,
        "est_valide": blockchain_instance.est_chaine_valide()
    }

@router.get("/blocks", response_model=List[BlockResponse])
async def get_blocks():
    """Retourne la liste complète des blocs."""
    # Note: On transforme les objets Block en dictionnaires compatibles avec le schéma
    blocks_data = []
    for b in blockchain_instance.chaine:
        blocks_data.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "transactions": [vars(t) for t in b.transactions],
            "previous_hash": b.previous_hash,
            "merkle_root": b.merkle_root,
            "nonce": b.nonce,
            "hash": b.hash
        })
    return blocks_data

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(tx_data: TransactionCreate):
    """Crée une nouvelle transaction et l'ajoute à la file d'attente."""
    # Conversion du secteur enum API vers enum Blockchain
    try:
        secteur_bc = BTSecteur[tx_data.secteur.name]
    except KeyError:
        raise HTTPException(status_code=400, detail="Secteur invalide")

    # Création de l'objet Transaction
    tx = Transaction(
        expediteur=tx_data.expediteur,
        destinataire=tx_data.destinataire,
        donnees=tx_data.donnees,
        secteur=secteur_bc,
        description=tx_data.description,
        montant=tx_data.montant
    )
    
    # On attache la signature fournie
    tx.signature = tx_data.signature
    
    # Validation et ajout
    if not blockchain_instance.ajouter_transaction(tx):
        raise HTTPException(status_code=400, detail="Transaction invalide (Signature ou intégrité)")
    
    return {
        "expediteur": tx.expediteur,
        "destinataire": tx.destinataire,
        "donnees": tx.donnees,
        "secteur": tx.secteur.value,
        "description": tx.description,
        "montant": tx.montant,
        "horodatage": tx.horodatage,
        "hash": tx.hash,
        "signature": tx.signature
    }

@router.get("/pending-transactions")
async def get_pending_transactions():
    """Retourne la liste des transactions en attente."""
    return [vars(tx) for tx in blockchain_instance.transactions_en_attente]

from src.api.deps import RoleChecker

@router.get("/brain-info")
async def get_brain_info():
    """Retourne les décisions apprises par l'IA (meilleur leader par état)."""
    brain_info = {}
    etat_map = {0: "Optimal", 1: "Dégradé", 2: "Critique"}
    
    for state, actions in brain.q_table.items():
        if actions:
            best_action = max(actions, key=actions.get)
            brain_info[etat_map.get(state, str(state))] = {
                "best_leader": f"NODE_{best_action}",
                "score": actions[best_action]
            }
    return brain_info

@router.get("/balance/{public_key}")
async def get_balance(public_key: str):
    """Calcule le solde d'un utilisateur à partir de la blockchain."""
    print(f" [DEBUG] get_balance appelé avec: '{public_key}'")
    # Normalisation pour gérer les formats tuple/chaîne
    normalized_key = Crypto.normalize_key(public_key)
    print(f" [DEBUG] Cle normalisée: '{normalized_key}'")
    solde = blockchain_instance.obtenir_solde(normalized_key)
    print(f" [DEBUG] Solde trouvé: {solde}")
    return {"balance": solde}

@router.get("/balance/history/{public_key}")
async def get_balance_history(public_key: str):
    """Récupère l'évolution du solde d'un utilisateur."""
    # Normalisation pour gérer les formats tuple/chaîne
    normalized_key = Crypto.normalize_key(public_key)
    return {"history": blockchain_instance.obtenir_historique_solde(normalized_key)}

@router.post("/mine", response_model=BlockResponse, dependencies=[Depends(RoleChecker(['MINEUR']))])
async def mine_block():
    """Lance le processus de minage, sélectionnant le leader via l'IA Q-Learning."""
    if not blockchain_instance.transactions_en_attente:
        raise HTTPException(status_code=400, detail="Aucune transaction en attente à miner")
    
    from src.api.instances import get_network_state_id
    
    try:
        # 1. Obtenir l'état contextuel du réseau (on prend le district 1 par défaut comme référence)
        state = get_network_state_id(1, len(blockchain_instance.transactions_en_attente))
        print(f" [DEBUG] État contextuel pour IA: {state}")
        
        # 2. Demander au cerveau de choisir un leader en fonction de cet état
        action = brain.choisir_action(state)
        leader_node = f"NODE_{action}"
        print(f" [DEBUG] Leader élu: {leader_node}")
        
        # 3. Minage avec le leader choisi
        nouveau_bloc = blockchain_instance.miner_transactions_en_attente(adresse_mineur=leader_node)
        
        # 4. Synchronisation de l'état applicatif
        if nouveau_bloc:
            instances = {
                "agriculture_manager": agriculture_manager,
                "foncier_uf": foncier_uf,
                "pending_land_requests": pending_land_requests,
                "diploma_manager": diploma_manager,
                "pending_diploma_requests": pending_diploma_requests,
                "microfinance_manager": microfinance_manager
            }
            
            synchronize_state(nouveau_bloc, instances)
        
        # 5. Récompenser le cerveau
        if nouveau_bloc:
            brain.mettre_a_jour(state, action, 10, get_network_state_id(1, len(blockchain_instance.transactions_en_attente)))
            print(f" [DEBUG] Minage réussi, récompense IA +10")
        else:
            brain.mettre_a_jour(state, action, -10, get_network_state_id(1, len(blockchain_instance.transactions_en_attente)))
            print(f" [DEBUG] Échec minage, récompense IA -10")
        
        # Sauvegarde du cerveau
        brain.sauvegarder_cerveau()
        
        # Sauvegarde de l'état après minage
        save_state(
            blockchain_instance, 
            foncier_uf, 
            pending_land_requests, 
            agriculture_manager.lots, 
            pending_diploma_requests,
            microfinance_manager.pending_transfers
        )
        
        return {
            "index": nouveau_bloc.index,
            "timestamp": nouveau_bloc.timestamp,
            "transactions": [vars(t) for t in nouveau_bloc.transactions],
            "previous_hash": nouveau_bloc.previous_hash,
            "merkle_root": nouveau_bloc.merkle_root,
            "nonce": nouveau_bloc.nonce,
            "hash": nouveau_bloc.hash,
            "leader_node": leader_node
        }
    except Exception as e:
        print(f" [!] ERREUR CRITIQUE DANS MINE_BLOCK: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne lors du minage: {str(e)}")

@router.get("/verify/{tx_hash}")
async def verify_transaction(tx_hash: str):
    """
    Vérifie si une transaction existe dans la blockchain et est valide.
    Simule la vérification via Arbre de Merkle.
    """
    for bloc in blockchain_instance.chaine:
        for tx in bloc.transactions:
            if tx.hash == tx_hash:
                return {
                    "status": "AUTHENTIQUE",
                    "transaction": {
                        "hash": tx.hash,
                        "secteur": tx.secteur.value,
                        "description": tx.description,
                        "horodatage": tx.horodatage
                    },
                    "bloc_index": bloc.index,
                    "merkle_root": bloc.merkle_root,
                    "confirmation": "Validé par le réseau Hazo Lova"
                }
    
    raise HTTPException(status_code=404, detail="Transaction non trouvée ou falsifiée")
