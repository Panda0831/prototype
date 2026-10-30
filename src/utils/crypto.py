import hashlib
import re
import secrets

import bcrypt
import ecdsa


class Crypto:
    """
    Une implémentation utilisant le module 'ecdsa' pour la signature numérique
    sur courbe elliptique (ECDSA) et 'bcrypt' pour la sécurité des mots de passe.
    """

    # Paramètres de la courbe SECP256k1 pour compatibilité
    N = ecdsa.SECP256k1.order
    P = ecdsa.SECP256k1.curve.p()
    G = (ecdsa.SECP256k1.generator.x(), ecdsa.SECP256k1.generator.y())

    @staticmethod
    # supprimant les caractères non alphanumériques et en convertissant en minuscules
    def normalize_key(key: str) -> str:
        """Nettoyage agressif des clés pour la comparaison entre différents formats."""
        if not key:
            return ""
        norm = re.sub(r"[^a-zA-Z0-9]", "", str(key)).lower()
        # print(f" [DEBUG] Normalisation: '{key}' -> '{norm}'")
        return norm

    @staticmethod
    def hacher_mot_de_passe(mot_de_passe: str) -> str:
        """Hache un mot de passe de manière sécurisée avec bcrypt."""
        # bcrypt attend des bytes
        password_bytes = mot_de_passe.encode("utf-8")
        salt = bcrypt.gensalt()  # génère un sel aléatoire
        hashed = bcrypt.hashpw(
            password_bytes, salt
        )  # hache le mot de passe avec le sel
        return hashed.decode("utf-8")

    @staticmethod
    def verifier_mot_de_passe(mot_de_passe_clair: str, mot_de_passe_hache: str) -> bool:
        """Vérifie si un mot de passe correspond à son empreinte hachée."""
        try:
            password_bytes = mot_de_passe_clair.encode("utf-8")
            hashed_bytes = mot_de_passe_hache.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def generer_paire_cles():
        """
        Génère une paire de clés cryptographiques.
        Retourne : (clé_privée_hex, (clé_publique_x_hex, clé_publique_y_hex))
        """
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.verifying_key

        # Formatage identique à l'ancienne version (hexadécimal avec préfixe 0x)
        cle_privee_int = int(sk.to_string().hex(), 16)
        point = vk.pubkey.point

        return hex(cle_privee_int), (hex(point.x()), hex(point.y()))

    @staticmethod
    def signer(cle_privee_hex, message):
        """
        Signe un message textuel avec la clé privée.
        Retourne une signature composée d'un couple (r, s) au format hexadécimal.
        """
        # Nettoyage de la clé hex (retrait du '0x' et padding)
        priv_hex = (
            cle_privee_hex[2:] if cle_privee_hex.startswith("0x") else cle_privee_hex
        )
        priv_hex = priv_hex.zfill(64)

        sk = ecdsa.SigningKey.from_string(
            bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1
        )

        # On signe le message (le module gère le hachage SHA-256 en interne si spécifié)
        signature_bytes = sk.sign(message.encode("utf-8"), hashfunc=hashlib.sha256)

        # Décodage pour obtenir r et s
        r, s = ecdsa.util.sigdecode_string(signature_bytes, ecdsa.SECP256k1.order)

        return hex(r), hex(s)

    @staticmethod
    def verifier(cle_publique_coords, message, signature_rs):
        """
        Vérifie l'authenticité d'une signature pour un message et une clé publique donnés.
        """
        try:
            # Reconstruction de la clé publique à partir des coordonnées
            x = int(cle_publique_coords[0], 16)
            y = int(cle_publique_coords[1], 16)

            point = ecdsa.ellipticcurve.Point(ecdsa.SECP256k1.curve, x, y)
            vk = ecdsa.VerifyingKey.from_public_point(point, curve=ecdsa.SECP256k1)

            # Reconstruction de la signature
            r = int(signature_rs[0], 16)
            s = int(signature_rs[1], 16)
            signature_bytes = ecdsa.util.sigencode_string(r, s, ecdsa.SECP256k1.order)

            return vk.verify(
                signature_bytes, message.encode("utf-8"), hashfunc=hashlib.sha256
            )
        except Exception:
            # En cas de n'importe quelle erreur (format, type, signature invalide), on retourne False
            return False

    @staticmethod
    def hacher_sha256(donnees):
        """
        Produit un condensat SHA-256 (hash) des données fournies.
        """
        return hashlib.sha256(donnees.encode("utf-8")).hexdigest()
