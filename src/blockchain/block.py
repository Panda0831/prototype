import time

from src.blockchain.merkle_tree import MerkleTree
from src.blockchain.transaction import Transaction
from src.utils.crypto import Crypto


class Block:
    """
    Représente un bloc dans la blockchain Hazo Lova.
    Contient un ensemble de transactions validées.
    """

    def __init__(self, index, transactions, previous_hash, nonce=0):
        """
        Initialise un nouveau bloc.

        :param index: Position du bloc dans la chaîne.
        :param transactions: Liste des transactions incluses dans le bloc.
        :param previous_hash: Empreinte numérique du bloc précédent.
        :param nonce: Nombre utilisé pour le minage (Proof of Work).
        """
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce

        # Calcul de la racine de Merkle pour résumer les transactions
        self.merkle_root = MerkleTree(transactions).obtenir_racine()

        # Hashage initial du bloc
        self.hash = self.calculer_hash()

    def calculer_hash(self):
        """
        Génère le hash SHA-256 du bloc à partir de ses composants.
        """
        contenu_bloc = (
            str(self.index)
            + str(self.timestamp)
            + str(self.merkle_root)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return Crypto.hacher_sha256(contenu_bloc)

    def miner(self, difficulte):
        """
        Algorithme de Proof of Work (Preuve de Travail).
        Incrémente le nonce jusqu'au hash cible.
        """
        cible = "0" * difficulte
        print(f" Minage du bloc {self.index} en cours (difficulté: {difficulte})...")

        while self.hash[:difficulte] != cible:
            self.nonce += 1
            self.hash = self.calculer_hash()

        print(f" Bloc miné ! Hash : {self.hash}")

    def __repr__(self):
        return f"Block(Index: {self.index}, Hash: {self.hash[:10]}..., Prev: {self.previous_hash[:10]}...)"

    @staticmethod
    def from_dict(data: dict):
        """Reconstruit un bloc à partir d'un dictionnaire."""
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        bloc = Block(
            index=data['index'],
            transactions=transactions,
            previous_hash=data['previous_hash'],
            nonce=data['nonce']
        )
        bloc.timestamp = data['timestamp']
        bloc.merkle_root = data['merkle_root']
        bloc.hash = data['hash']
        return bloc

    def to_dict(self):
        """Convertit le bloc en dictionnaire pour propagation réseau."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root,
            "hash": self.hash
        }
