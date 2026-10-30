from typing import List, Dict
from src.utils.crypto import Crypto


class MerkleTree:
    """
    Implémentation d'un Arbre de Merkle pour regrouper les transactions d'un bloc.
    Permet de vérifier l'intégrité des transactions de manière efficace.
    """

    def __init__(self, transactions):
        """
        Construit l'arbre de Merkle à partir d'une liste de transactions.

        :param transactions: Liste d'objets Transaction.
        """
        self.transactions = transactions
        self.root = None
        # extraction des hashes des transactions
        if transactions:
            self.root = self._construire_racine([tx.hash for tx in transactions])

    def _construire_racine(self, hashes):
        """
        Méthode récursive pour calculer la racine de l'arbre.
        """
        nombre_hashes = len(hashes)

        if nombre_hashes == 0:
            return None
        if nombre_hashes == 1:
            return hashes[0]

        nouveaux_hashes = []

        # Parcourir les hashes deux par deux
        for i in range(0, nombre_hashes, 2):
            hash1 = hashes[i]
            # Si c'est le dernier hash et qu'il est seul, on le duplique
            if i + 1 < nombre_hashes:
                hash2 = hashes[i + 1]
            else:
                hash2 = hashes[i]

            # Combiner les deux hashes et hacher le résultat
            hash_combine = Crypto.hacher_sha256(hash1 + hash2)
            nouveaux_hashes.append(hash_combine)

        return self._construire_racine(nouveaux_hashes)

    def get_proof(self, index: int) -> List[Dict[str, str]]:
        """Génère la preuve de Merkle pour une transaction à un index donné."""
        hashes = [tx.hash for tx in self.transactions]
        proof = []

        current_layer = hashes
        while len(current_layer) > 1:
            if index % 2 == 0:
                # Si index pair, le voisin est index+1
                neighbor_idx = index + 1 if index + 1 < len(current_layer) else index
                proof.append({"position": "right", "hash": current_layer[neighbor_idx]})
            else:
                # Si index impair, le voisin est index-1
                neighbor_idx = index - 1
                proof.append({"position": "left", "hash": current_layer[neighbor_idx]})

            # Passer à la couche supérieure
            new_layer = []
            for i in range(0, len(current_layer), 2):
                h1 = current_layer[i]
                h2 = current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]
                new_layer.append(Crypto.hacher_sha256(h1 + h2))

            current_layer = new_layer
            index //= 2

        return proof

    def obtenir_racine(self):
        """Retourne la racine de l'arbre de Merkle (Merkle Root)."""
        return self.root
