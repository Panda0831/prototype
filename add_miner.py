from src.db.session import SessionLocal
from src.db.models import User
import bcrypt

def add_miner():
    print("Tentative d'ajout de l'utilisateur Mineur...")
    db = SessionLocal()
    # Utilise la clé publique utilisée dans le script de test
    miner_pub_key = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    
    miner = db.query(User).filter(User.public_key == miner_pub_key).first()
    
    if not miner:
        new_miner = User(
            username="TestMineur",
            email="miner@hazolova.mg",
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode('utf-8'),
            role="MINEUR",
            district="Antananarivo",
            public_key=miner_pub_key
        )
        db.add(new_miner)
        db.commit()
        print(" [!] Utilisateur Mineur ajouté avec succès.")
    else:
        # Si l'utilisateur existe déjà, on s'assure qu'il a le rôle MINEUR
        miner.role = "MINEUR"
        db.commit()
        print(" [!] Utilisateur existant mis à jour avec le rôle MINEUR.")
    
    db.close()

if __name__ == "__main__":
    add_miner()
