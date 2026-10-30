import pytest
from src.blockchain.transaction import Transaction, SecteurActivite
from src.utils.crypto import Crypto

def test_creation_transaction():
    """Vérifie que les champs d'une transaction sont correctement initialisés."""
    _, publique = Crypto.generer_paire_cles()
    _, destinataire_publique = Crypto.generer_paire_cles()
    
    desc = "Certification du diplôme de Master 2"
    tx = Transaction(
        expediteur=publique,
        destinataire=destinataire_publique,
        donnees={"id_diplome": "M2-2026-001", "grade": "Master"},
        secteur=SecteurActivite.DIPLOME,
        description=desc
    )
    
    assert tx.expediteur == publique
    assert tx.description == desc
    assert tx.hash is not None
    assert tx.signature is None

def test_cycle_signature_et_validation():
    """Vérifie qu'une transaction signée correctement est valide."""
    privee, publique = Crypto.generer_paire_cles()
    _, destinataire_publique = Crypto.generer_paire_cles()
    
    tx = Transaction(
        expediteur=publique,
        destinataire=destinataire_publique,
        donnees="500kg de Vanille Bourbon",
        secteur=SecteurActivite.PRODUITS_AGRICOLES,
        description="Vente Antalaha - Export"
    )
    
    # Signature
    tx.signer(privee)
    assert tx.signature is not None
    
    # Validation
    assert tx.est_valide() is True

def test_transaction_invalide_si_alteree():
    """Vérifie qu'une transaction dont les données changent après signature est invalide."""
    privee, publique = Crypto.generer_paire_cles()
    _, publique_dest = Crypto.generer_paire_cles()
    
    tx = Transaction(publique, publique_dest, "100 MGA", SecteurActivite.MICROFINANCE, "Crédit Agricole")
    tx.signer(privee)
    
    # Tentative de modification des données (fraude)
    tx.donnees = "5000 MGA"
    
    # La transaction ne doit plus être valide car le hash ne correspond plus
    assert tx.est_valide() is False

def test_transaction_invalide_sans_signature():
    """Vérifie qu'une transaction non signée est invalide."""
    _, publique = Crypto.generer_paire_cles()
    _, publique_dest = Crypto.generer_paire_cles()
    
    tx = Transaction(publique, publique_dest, "Terrain A1", SecteurActivite.FONCIER, "Titre foncier")
    
    assert tx.est_valide() is False
