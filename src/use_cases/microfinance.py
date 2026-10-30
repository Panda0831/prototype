from typing import List, Dict, Optional
import time
from src.blockchain.transaction import Transaction, SecteurActivite

class MicrofinanceManager:
    """
    Gère les transactions financières et les micro-prêts.
    Workflow : Envoi -> Attente -> Acceptation -> Blockchain.
    """
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.pending_transfers: List[dict] = []

    def create_transfer_request(self, sender_id: str, receiver_id: str, amount: float, description: str):
        """
        Initialise une demande de transfert d'argent sur la blockchain.
        La demande doit être minée pour apparaître dans les attentes du destinataire.
        """
        # Vérification du solde de l'expéditeur
        solde_actuel = self.blockchain.obtenir_solde(sender_id)
        if solde_actuel < amount:
            return None # Le controleur gérera l'erreur 400
            
        transfer_id = int(time.time() * 1000)
        
        tx = Transaction(
            expediteur=sender_id,
            destinataire=receiver_id,
            donnees={
                "transfer_id": transfer_id, 
                "type": "MICRO_TRANSFER_REQUEST",
                "amount": amount,
                "description": description
            },
            secteur=SecteurActivite.MICROFINANCE,
            description=f"Demande de transfert : {amount} MGA pour {description}",
            montant=0 # Le montant n'est pas encore débité
        )
        tx.signature = "SIG_FINANCE_DEMO"
        
        if self.blockchain.ajouter_transaction(tx):
            print(f" [DEBUG] Demande de transfert {transfer_id} ajoutée au mempool")
            transfer_obj = {
                "id": transfer_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "amount": amount,
                "description": description,
                "status": "IN_BLOCKCHAIN_PENDING_MINING"
            }
            self.pending_transfers.append(transfer_obj)
            return transfer_obj
        return None

    def accept_transfer(self, transfer_id: int):
        """Le destinataire accepte l'argent, déclenchant l'inscription blockchain."""
        transfer = next((t for t in self.pending_transfers if t["id"] == transfer_id), None)
        
        if not transfer:
            return None, "Transfert non trouvé"
            
        # Re-vérification du solde au moment de l'acceptation
        solde_expediteur = self.blockchain.obtenir_solde(transfer["sender_id"])
        if solde_expediteur < transfer["amount"]:
            return None, "L'expéditeur n'a plus assez de fonds pour honorer ce transfert."

        # Création de la transaction officielle sur la blockchain
        tx = Transaction(
            expediteur=transfer["sender_id"],
            destinataire=transfer["receiver_id"],
            donnees={"transfer_id": transfer_id, "type": "MICRO_TRANSFER"},
            secteur=SecteurActivite.MICROFINANCE,
            description=transfer["description"],
            montant=transfer["amount"]
        )
        
        # On utilise une signature de démo
        tx.signature = "SIG_FINANCE_DEMO"
        
        if self.blockchain.ajouter_transaction(tx):
            # Marquer comme complété et retirer de la liste pending est fait au minage
            transfer["status"] = "IN_BLOCKCHAIN_PENDING_MINING"
            transfer["tx_hash"] = tx.hash
            
            return transfer, None
            
        return None, "Erreur lors de l'ajout à la blockchain"

    def get_pending_for_user(self, user_id: str):
        """
        Récupère les transferts qu'un utilisateur doit valider (en tant que destinataire).
        Utilise la normalisation pour une comparaison robuste.
        """
        import re
        def normalize(k): return re.sub(r'[^a-zA-Z0-9]', '', str(k)).lower()
        
        target_key = normalize(user_id)
        # On filtre par receiver_id car c'est le destinataire qui accepte
        return [t for t in self.pending_transfers if normalize(t["receiver_id"]) == target_key]
