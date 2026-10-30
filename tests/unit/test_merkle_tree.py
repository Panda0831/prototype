import pytest
from src.blockchain.merkle_tree import MerkleTree
from src.blockchain.transaction import Transaction, SecteurActivite
from src.utils.crypto import Crypto

def creer_tx_test(donnees):
    """Utilitaire pour créer une transaction de test rapidement."""
    _, pub = Crypto.generer_paire_cles()
    return Transaction(pub, pub, donnees, SecteurActivite.PAIEMENT)

def test_merkle_vide():
    """Vérifie qu'une liste vide retourne une racine None."""
    tree = MerkleTree([])
    assert tree.obtenir_racine() is None

def test_merkle_unique():
    """Vérifie qu'une seule transaction donne son propre hash comme racine."""
    tx = creer_tx_test("Transaction Unique")
    tree = MerkleTree([tx])
    assert tree.obtenir_racine() == tx.hash

def test_merkle_pair():
    """Vérifie le calcul de la racine pour 2 transactions."""
    tx1 = creer_tx_test("TX1")
    tx2 = creer_tx_test("TX2")
    tree = MerkleTree([tx1, tx2])
    
    # La racine doit être H(H1 + H2)
    hash_attendu = Crypto.hacher_sha256(tx1.hash + tx2.hash)
    assert tree.obtenir_racine() == hash_attendu

def test_merkle_impair():
    """
    Vérifie le calcul pour 3 transactions (nombre impair).
    La dernière transaction doit être dupliquée pour l'appairage.
    """
    tx1 = creer_tx_test("TX1")
    tx2 = creer_tx_test("TX2")
    tx3 = creer_tx_test("TX3")
    tree = MerkleTree([tx1, tx2, tx3])
    
    # Niveau 1 :
    # H12 = H(H1 + H2)
    # H33 = H(H3 + H3)  <- Duplication car impair
    h12 = Crypto.hacher_sha256(tx1.hash + tx2.hash)
    h33 = Crypto.hacher_sha256(tx3.hash + tx3.hash)
    
    # Racine : H(H12 + H33)
    racine_attendue = Crypto.hacher_sha256(h12 + h33)
    
    assert tree.obtenir_racine() == racine_attendue

def test_merkle_quatre_transactions():
    """Vérifie le calcul pour 4 transactions (arbre équilibré)."""
    txs = [creer_tx_test(f"TX{i}") for i in range(4)]
    tree = MerkleTree(txs)
    
    h01 = Crypto.hacher_sha256(txs[0].hash + txs[1].hash)
    h23 = Crypto.hacher_sha256(txs[2].hash + txs[3].hash)
    racine_attendue = Crypto.hacher_sha256(h01 + h23)
    
    assert tree.obtenir_racine() == racine_attendue

def test_merkle_integrite():
    """Vérifie que changer une donnée change la racine."""
    tx1 = creer_tx_test("TX1")
    tx2 = creer_tx_test("TX2")
    
    tree_original = MerkleTree([tx1, tx2])
    racine_initiale = tree_original.obtenir_racine()
    
    # On modifie tx1 (en recréant une transaction avec le même objet pour simuler une altération)
    tx1.donnees = "TX1 MODIFIEE"
    tx1.hash = tx1.calculer_hash()
    
    tree_modifie = MerkleTree([tx1, tx2])
    assert tree_modifie.obtenir_racine() != racine_initiale
