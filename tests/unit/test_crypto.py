import pytest
from src.utils.crypto import Crypto

def test_hachage_sha256():
    """Vérifie que le hachage SHA-256 est correct et cohérent."""
    message = "Hazo Lova 2035"
    h1 = Crypto.hacher_sha256(message)
    h2 = Crypto.hacher_sha256(message)
    
    assert h1 == h2
    assert len(h1) == 64 # SHA-256 produit 256 bits (64 caractères hex)
    assert h1 != Crypto.hacher_sha256("Autre message")

def test_generation_cles():
    """Vérifie la génération d'une paire de clés valide."""
    privee, publique = Crypto.generer_paire_cles()
    
    assert privee.startswith("0x")
    assert isinstance(publique, tuple)
    assert len(publique) == 2
    assert publique[0].startswith("0x")
    assert publique[1].startswith("0x")

def test_signature_et_verification_valide():
    """Vérifie qu'une signature valide est acceptée."""
    privee, publique = Crypto.generer_paire_cles()
    message = "Transaction de vanille entre Antalaha et Tamatave"
    
    signature = Crypto.signer(privee, message)
    
    est_valide = Crypto.verifier(publique, message, signature)
    assert est_valide is True

def test_signature_invalide_mauvais_message():
    """Vérifie qu'une signature est refusée si le message a été altéré."""
    privee, publique = Crypto.generer_paire_cles()
    message_original = "Paiement de 1000 MGA"
    message_altere = "Paiement de 5000 MGA"
    
    signature = Crypto.signer(privee, message_original)
    
    est_valide = Crypto.verifier(publique, message_altere, signature)
    assert est_valide is False

def test_signature_invalide_mauvaise_cle():
    """Vérifie qu'une signature est refusée si la clé publique ne correspond pas."""
    privee_a, publique_a = Crypto.generer_paire_cles()
    privee_b, publique_b = Crypto.generer_paire_cles()
    message = "Diplôme certifié par l'ESMIA"
    
    signature = Crypto.signer(privee_a, message)
    
    # Vérification avec la clé publique de B au lieu de A
    est_valide = Crypto.verifier(publique_b, message, signature)
    assert est_valide is False
