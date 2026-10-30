from typing import List, Dict
from src.blockchain.transaction import Transaction, SecteurActivite
from src.blockchain.merkle_tree import MerkleTree

class DiplomaManager:
    """
    Gère la certification des diplômes sur la blockchain Hazo Lova.
    Utilise des preuves de Merkle pour valider l'authenticité.
    """
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.diplomas: Dict[str, dict] = {} # diploma_id -> info

    def register_diploma(self, student_id: str, degree_title: str, university: str, year: int, document_hash: str = None):
        """Enregistre un diplôme sur la blockchain avec son hash de document."""
        diploma_id = f"DIP-{student_id}-{year}"
        
        diploma_data = {
            "student_id": student_id,
            "title": degree_title,
            "university": university,
            "year": year,
            "document_hash": document_hash
        }
        
        tx = Transaction(
            expediteur="UNIVERSITE_SYSTEM",
            destinataire=student_id,
            donnees=diploma_data,
            secteur=SecteurActivite.DIPLOME,
            description=f"Diplôme {degree_title} certifié (Hash PDF: {document_hash[:10] if document_hash else 'N/A'})",
            montant=0
        )
        tx.signature = "SIG_ADMIN_DIPLOME"
        
        if self.blockchain.ajouter_transaction(tx):
            # self.diplomas[diploma_id] = diploma_data <-- SUPPRIMÉ
            return diploma_id
        return None

    def get_diploma_proof(self, diploma_id: str):
        """
        Génère la preuve de Merkle pour un diplôme donné.
        """
        # 1. Trouver la transaction correspondant au diplôme
        target_tx = None
        target_block = None
        
        # Log pour déboguer
        print(f" [DEBUG] Searching proof for: {diploma_id}")
        
        for block in self.blockchain.chaine:
            for tx in block.transactions:
                if tx.secteur == SecteurActivite.DIPLOME:
                    # Safely parse donnees if it's a string
                    data = tx.donnees
                    if isinstance(data, str):
                        import json
                        try: data = json.loads(data)
                        except: data = {}
                    
                    # Construct a temporary diploma_id to match the one in register_diploma
                    student_id = data.get("student_id", "")
                    year = data.get("year", "")
                    generated_id = f"DIP-{student_id}-{year}"
                    print(f" [DEBUG] Comparing {diploma_id} with {generated_id}")
                    
                    if generated_id == diploma_id:
                        target_tx = tx
                        target_block = block
                        print(f" [DEBUG] Found matching tx: {tx.hash}")
                        break
            if target_tx: break
        
        if not target_tx or not target_block:
            print(f" [DEBUG] Proof NOT found for {diploma_id}")
            return None
            
        # 2. Générer la preuve
        tree = MerkleTree(target_block.transactions)
        tx_index = target_block.transactions.index(target_tx)
        proof = tree.get_proof(tx_index)
        
        return {
            "root": tree.root,
            "proof": proof,
            "tx_hash": target_tx.hash
        }
