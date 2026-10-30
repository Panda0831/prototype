from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from src.blockchain.transaction import SecteurActivite, Transaction
from src.utils.crypto import Crypto


class RoleActeur(Enum):
    UNIVERSITE = "UNIVERSITE"  # Émetteur de diplômes
    AGENCE_FONCIERE = "FONCIER"  # Gestion des titres de propriété
    EXPORTATEUR = "EXPORTATEUR"  # Acheteur/Exportateur de produits agricoles
    RECOLTEUR = "RECOLTEUR"  # Producteur local
    INSTITUT_MICROFINANCE = "IMF"  # Émetteur de micro-crédits
    CITOYEN = "CITOYEN"  # Utilisateur final / Client
    MINEUR = "MINEUR"  # Validateur du réseau
    ADMIN = "ADMIN"  # Administrateur système


@dataclass
class Acteur:
    """
    Représente un participant (individu ou organisation) dans le réseau Madagascar 2035.
    Chaque acteur possède une identité cryptographique.
    """

    nom: str
    role: RoleActeur
    district: str

    # Identité cryptographique
    cle_privee: str = field(init=False, repr=False)
    cle_publique: str = field(init=False)

    # Historique local des transactions émises/reçues
    historique_transactions: List[str] = field(default_factory=list, init=False)

    # e
    def __post_init__(self):
        """Génère automatiquement la paire de clés lors de la création de l'acteur."""
        self.cle_privee, self.cle_publique = Crypto.generer_paire_cles()

    def creer_transaction(
        self, destinataire_cle_pub, donnees, secteur, description="", montant=0
    ):
        """
        Crée, signe et retourne une nouvelle transaction.
        """
        transaction = Transaction(
            expediteur=self.cle_publique,
            destinataire=destinataire_cle_pub,
            donnees=donnees,
            secteur=secteur,
            description=description,
            montant=montant,
        )

        # L'acteur signe la transaction avec sa propre clé privée
        transaction.signer(self.cle_privee)

        self.historique_transactions.append(transaction.hash)

        return transaction
        # __repr__ est une méthode spéciale qui définit la représentation en chaîne de caractères d'un objet.

    def __repr__(self):
        return f"Acteur({self.nom}, Role: {self.role.value}, District: {self.district})"
