import pytest
from src.blockchain.blockchain import Blockchain
from src.blockchain.transaction import Transaction, SecteurActivite
from src.utils.crypto import Crypto

def test_blockchain_initialization():
    """Vérifie que la blockchain commence avec le bloc genèse."""
    bc = Blockchain()
    assert len(bc.chaine) == 1
    assert bc.chaine[0].index == 0
    assert bc.chaine[0].previous_hash == "0" * 64

def test_ajouter_transaction_valide():
    """Vérifie l'ajout d'une transaction valide à la file d'attente."""
    bc = Blockchain()
    privee, publique = Crypto.generer_paire_cles()
    _, dest_publique = Crypto.generer_paire_cles()
    
    tx = Transaction(publique, dest_publique, "Data", SecteurActivite.PRODUITS_AGRICOLES)
    tx.signer(privee)
    
    success = bc.ajouter_transaction(tx)
    assert success is True
    assert len(bc.transactions_en_attente) == 1

def test_ajouter_transaction_invalide():
    """Vérifie qu'une transaction non signée est refusée."""
    bc = Blockchain()
    _, publique = Crypto.generer_paire_cles()
    _, dest_publique = Crypto.generer_paire_cles()
    
    tx = Transaction(publique, dest_publique, "Data", SecteurActivite.PRODUITS_AGRICOLES)
    # Pas de signature
    
    success = bc.ajouter_transaction(tx)
    assert success is False
    assert len(bc.transactions_en_attente) == 0

def test_minage_et_recompense():
    """Vérifie que le minage crée un bloc et attribue une récompense."""
    bc = Blockchain()
    bc.difficulte = 1 # Difficulté basse pour le test
    
    privee, publique = Crypto.generer_paire_cles()
    _, mineur_publique = Crypto.generer_paire_cles()
    _, dest_publique = Crypto.generer_paire_cles()
    
    # Correction : passer le montant explicitement
    tx = Transaction(publique, dest_publique, "Data", SecteurActivite.PAIEMENT, montant=100)
    tx.signer(privee)
    bc.ajouter_transaction(tx)
    
    bc.miner_transactions_en_attente(mineur_publique)
    
    assert len(bc.chaine) == 2
    assert bc.obtenir_solde(mineur_publique) == bc.recompense_minage
    assert bc.obtenir_solde(publique) == -100
    assert bc.obtenir_solde(dest_publique) == 100

def test_validite_chaine():
    """Vérifie que la validation de la chaîne fonctionne."""
    bc = Blockchain()
    bc.difficulte = 1
    
    privee, publique = Crypto.generer_paire_cles()
    _, mineur_publique = Crypto.generer_paire_cles()
    
    tx = Transaction(publique, mineur_publique, "Paiement", SecteurActivite.PAIEMENT, montant=50)
    tx.signer(privee)
    bc.ajouter_transaction(tx)
    bc.miner_transactions_en_attente(mineur_publique)
    
    assert bc.est_chaine_valide() is True
    
    # Altération frauduleuse (on modifie la transaction de l'utilisateur, pas la récompense)
    # Dans miner_transactions_en_attente, la récompense est à l'index 0
    bc.chaine[1].transactions[1].montant = 1000000
    
    assert bc.est_chaine_valide() is False

def test_obtenir_dernier_bloc():
    """Vérifie que obtenir_dernier_bloc retourne bien le dernier bloc."""
    bc = Blockchain()
    assert bc.obtenir_dernier_bloc().index == 0
    
    bc.difficulte = 1
    _, mineur_publique = Crypto.generer_paire_cles()
    bc.miner_transactions_en_attente(mineur_publique)
    
    assert bc.obtenir_dernier_bloc().index == 1

def test_corruption_lien_blockchain():
    """Vérifie que la blockchain détecte une rupture de lien (previous_hash)."""
    bc = Blockchain()
    bc.difficulte = 1
    _, mineur_publique = Crypto.generer_paire_cles()
    
    bc.miner_transactions_en_attente(mineur_publique)
    bc.miner_transactions_en_attente(mineur_publique)
    
    assert bc.est_chaine_valide() is True
    
    # Rupture du lien entre le bloc 1 et le bloc 2
    bc.chaine[2].previous_hash = "fake_hash"
    
    assert bc.est_chaine_valide() is False

def test_corruption_hash_bloc():
    """Vérifie que la blockchain détecte si le hash d'un bloc ne correspond plus à son contenu."""
    bc = Blockchain()
    bc.difficulte = 1
    _, mineur_publique = Crypto.generer_paire_cles()
    
    bc.miner_transactions_en_attente(mineur_publique)
    
    assert bc.est_chaine_valide() is True
    
    # On change le hash du bloc manuellement sans changer le contenu
    bc.chaine[1].hash = "a" * 64
    
    assert bc.est_chaine_valide() is False
