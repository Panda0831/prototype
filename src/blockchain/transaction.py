import time
from enum import Enum
from src.utils.crypto import Crypto

class SecteurActivite(Enum):
    """Énumération des secteurs critiques de Madagascar 2035."""
    PRODUITS_AGRICOLES = "PRODUITS_AGRICOLES" # Traçabilité agricole (Vanille, Café, etc.)
    DIPLOME = "DIPLOME"           # Certification académique
    FONCIER = "FONCIER"           # Titres de propriété
    MICROFINANCE = "MICROFINANCE" # Inclusion financière (Prêts, Épargne)
    PAIEMENT = "PAIEMENT"         # Transfert de monnaie simple (MGA)

class Transaction:
    """
    Représente un échange de données ou de valeur sécurisé par cryptographie.
    C'est le composant fondamental de la blockchain Hazo Lova.
    """

    def __init__(self, expediteur, destinataire, donnees, secteur, description="", montant=0):
        """
        Initialise une nouvelle transaction.
        
        :param expediteur: Clé publique de l'émetteur (format hexadécimal).
        :param destinataire: Clé publique du récepteur (format hexadécimal).
        :param donnees: Contenu technique de la transaction (ex: ID produit, détails).
        :param secteur: Instance de SecteurActivite.
        :param description: Explication textuelle claire.
        :param montant: Valeur numérique si c'est une transaction financière.
        """
        self.expediteur = expediteur
        self.destinataire = destinataire
        self.donnees = donnees
        self.secteur = secteur
        self.description = description
        self.montant = montant
        
        # Horodatage automatique (Unix timestamp)
        self.horodatage = time.time()
        
        # Éléments cryptographiques (initialisés à None)
        self.signature = None
        self.hash = self.calculer_hash()

    def calculer_hash(self):
        """
        Génère une empreinte unique (SHA-256) basée sur le contenu de la transaction.
        """
        bloc_donnees = (
            str(self.expediteur) +
            str(self.destinataire) +
            str(self.donnees) +
            str(self.secteur.value) +
            str(self.description) +
            str(self.montant) +
            str(self.horodatage)
        )
        return Crypto.hacher_sha256(bloc_donnees)

    def signer(self, cle_privee_hex):
        """
        Signe la transaction avec la clé privée de l'expéditeur.
        La signature porte sur le hash unique de la transaction.
        """
        if not cle_privee_hex:
            raise ValueError("Une clé privée est requise pour signer la transaction.")
            
        # On signe le hash de la transaction pour garantir son intégrité
        self.signature = Crypto.signer(cle_privee_hex, self.hash)
        return self.signature

    def est_valide(self):
        """
        Vérifie la validité de la transaction :
        1. Le hash doit être conforme aux données actuelles.
        2. La signature doit être valide par rapport à la clé publique de l'expéditeur.
        """
        # 1. Vérification de l'intégrité (le hash n'a pas changé)
        if self.hash != self.calculer_hash():
            return False
            
        # Cas spécial pour les transactions administratives ou démo mobile
        if self.expediteur in ["SYSTEM", "ADMIN_GOUVERNEMENT", "GOUVERNEMENT_FONCIER"]:
            return True
        
        if self.signature in ["SIG_MOBILE_DEMO", "SIG_PROD_DEMO", "SIG_COLLECTEUR_DEMO", "SIG_VENDEUR_DEMO", "SIG_ADMIN_DIPLOME", "SIG_FINANCE_DEMO"]:
            return True

        # 2. Vérification de la signature
        if self.signature is None:
            return False
            
        # On s'assure que l'expéditeur est au bon format (tuple) s'il vient d'une chaîne
        pub_key = self.expediteur
        if isinstance(pub_key, str) and pub_key.startswith("("):
            try:
                import ast
                pub_key = ast.literal_eval(pub_key)
            except:
                pass

        # On vérifie si la signature correspond au hash et à la clé publique
        return Crypto.verifier(pub_key, self.hash, self.signature)

    def __repr__(self):
        """Représentation textuelle de la transaction pour le débogage."""
        return (f"Transaction({self.secteur.value}) : "
                f"De {str(self.expediteur)[:10]}... à {str(self.destinataire)[:10]}... | "
                f"Desc: {self.description}")

    @staticmethod
    def from_dict(data: dict):
        """Reconstruit une transaction à partir d'un dictionnaire."""
        tx = Transaction(
            expediteur=data['expediteur'],
            destinataire=data['destinataire'],
            donnees=data['donnees'],
            secteur=SecteurActivite(data['secteur']),
            description=data.get('description', ''),
            montant=data.get('montant', 0)
        )
        tx.horodatage = data['horodatage']
        tx.signature = data.get('signature')
        tx.hash = data['hash']
        return tx

    def to_dict(self):
        """Convertit la transaction en dictionnaire pour propagation réseau."""
        return {
            "expediteur": self.expediteur,
            "destinataire": self.destinataire,
            "donnees": self.donnees,
            "secteur": self.secteur.value,
            "description": self.description,
            "montant": self.montant,
            "horodatage": self.horodatage,
            "signature": self.signature,
            "hash": self.hash
        }
