from src.blockchain.block import Block
from src.blockchain.transaction import Transaction, SecteurActivite
from src.utils.crypto import Crypto

class Blockchain:
    """
    Gère la chaîne de blocs, la validation des transactions et le minage.
    La Blockchain est le registre décentralisé de Hazo Lova.
    """

    def __init__(self):
        """
        Initialise la blockchain avec le bloc genèse.
        """
        self.chaine = []
        self.transactions_en_attente = []
        self.difficulte = 4  # Ajustable selon la puissance de calcul souhaitée
        self.recompense_minage = 50.0 # Récompense symbolique en MGA
        
        self.creer_bloc_genese()

    def creer_bloc_genese(self):
        """
        Crée le tout premier bloc de la chaîne (Block #0).
        """
        bloc_genese = Block(
            index=0, 
            transactions=[], 
            previous_hash="0" * 64 # Hash fictif pour le début
        )
        self.chaine.append(bloc_genese)

    def obtenir_dernier_bloc(self):
        """
        Retourne le bloc le plus récent de la chaîne.
        """
        return self.chaine[-1]

    def ajouter_transaction(self, transaction):
        """
        Ajoute une transaction à la file d'attente après vérification.
        
        :param transaction: Instance de Transaction.
        :return: True si ajoutée, False sinon.
        """
        if not transaction.est_valide():
            print(f" [!] Transaction REJETÉE : {transaction.description} (Exp: {transaction.expediteur}, Sig: {transaction.signature})")
            return False
            
        self.transactions_en_attente.append(transaction)
        return True

    def miner_transactions_en_attente(self, adresse_mineur):
        """
        Crée un nouveau bloc contenant les transactions en attente,
        inclut une récompense pour le mineur, et lance le Proof of Work.
        
        :param adresse_mineur: Clé publique de celui qui mine le bloc.
        :return: Le nouveau bloc miné.
        """
        # 1. Création de la transaction de récompense (Coinbase)
        # Note: 'SYSTEM' est un expéditeur spécial qui n'a pas besoin de signature
        recompense = Transaction(
            expediteur="SYSTEM",
            destinataire=adresse_mineur,
            donnees="REWARD_MINING",
            secteur=SecteurActivite.PAIEMENT,
            description=f"Récompense pour le minage du bloc {len(self.chaine)}",
            montant=self.recompense_minage
        )
        
        # On ajoute la récompense en premier
        self.transactions_en_attente.insert(0, recompense)

        # 2. Création du bloc
        nouveau_bloc = Block(
            index=len(self.chaine),
            transactions=self.transactions_en_attente,
            previous_hash=self.obtenir_dernier_bloc().hash
        )

        # 3. Minage (Proof of Work)
        nouveau_bloc.miner(self.difficulte)
        
        # 4. Ajout à la chaîne
        self.chaine.append(nouveau_bloc)

        # 5. Réinitialisation des transactions en attente
        self.transactions_en_attente = []
        
        return nouveau_bloc

    def est_chaine_valide(self):
        """
        Vérifie si la blockchain est intègre et n'a pas été altérée.
        """
        for i in range(1, len(self.chaine)):
            bloc_actuel = self.chaine[i]
            bloc_precedent = self.chaine[i - 1]

            # Vérification du hash du bloc lui-même
            if bloc_actuel.hash != bloc_actuel.calculer_hash():
                print(f" [!] Hash corrompu au bloc {i}")
                return False

            # Vérification de la continuité de la chaîne
            if bloc_actuel.previous_hash != bloc_precedent.hash:
                print(f" [!] Lien rompu entre bloc {i-1} et bloc {i}")
                return False
                
            # Vérification de la validité des transactions à l'intérieur du bloc
            for tx in bloc_actuel.transactions:
                # On ignore la signature pour les transactions SYSTEM
                if tx.expediteur == "SYSTEM":
                    if tx.hash != tx.calculer_hash():
                        return False
                elif not tx.est_valide():
                    print(f" [!] Transaction invalide détectée dans le bloc {i}")
                    return False

        return True

    def obtenir_solde(self, adresse):
        """
        Parcourt toute la chaîne pour calculer le solde d'une adresse publique.
        """
        solde = 0.0
        adresse_norm = Crypto.normalize_key(adresse)
        for bloc in self.chaine:
            for tx in bloc.transactions:
                if Crypto.normalize_key(tx.expediteur) == adresse_norm:
                    solde -= tx.montant
                if Crypto.normalize_key(tx.destinataire) == adresse_norm:
                    solde += tx.montant
        return solde

    def obtenir_historique_solde(self, adresse):
        """
        Retourne l'évolution du solde d'une adresse au fil du temps (par bloc).
        """
        historique = [0.0]
        solde_courant = 0.0
        adresse_norm = Crypto.normalize_key(adresse)
        for bloc in self.chaine:
            a_bouge = False
            for tx in bloc.transactions:
                if Crypto.normalize_key(tx.expediteur) == adresse_norm:
                    solde_courant -= tx.montant
                    a_bouge = True
                if Crypto.normalize_key(tx.destinataire) == adresse_norm:
                    solde_courant += tx.montant
                    a_bouge = True
            if a_bouge:
                historique.append(solde_courant)
        
        if len(historique) < 2:
            historique.append(solde_courant)
            
        return historique

    def __repr__(self):
        return f"Blockchain(Blocks: {len(self.chaine)}, Pending: {len(self.transactions_en_attente)})"
