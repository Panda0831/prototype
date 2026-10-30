import requests
import time
import random

# Configuration
NODE_A = "http://localhost:8000"

def train_brain():
    print("--- DÉBUT DE L'ENTRAÎNEMENT DU CERVEAU (QLearning) ---")
    
    # Simuler 50 cycles de transaction + minage
    for i in range(50):
        print(f"Cycle {i+1}/50...")
        
        # 1. Ajouter une transaction aléatoire
        tx = {
            "expediteur": "ADMIN_GOUVERNEMENT",
            "destinataire": f"CITOYEN_{random.randint(1, 100)}",
            "donnees": "TX_DATA_TRAIN",
            "secteur": "FONCIER",
            "description": "Transaction de test pour entraînement",
            "montant": 0,
            "signature": "SIG_PROD_DEMO"
        }
        requests.post(f"{NODE_A}/api/blockchain/transactions", json=tx)
        
        # 2. Lancer le minage (ce qui déclenche l'IA Q-Learning)
        try:
            # Envoi avec une clé publique valide supposée
            headers = {"public-key": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}
            resp = requests.post(f"{NODE_A}/api/blockchain/mine", headers=headers)
            if resp.status_code == 200:
                print(f" -> Bloc miné avec succès par le leader choisi par IA.")
            else:
                print(f" -> Erreur minage ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f" -> Erreur de connexion: {e}")
        
        time.sleep(0.5)

    print("--- ENTRAÎNEMENT TERMINÉ ---")

if __name__ == "__main__":
    train_brain()
