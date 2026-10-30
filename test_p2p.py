import requests
import time

# Configuration
NODE_A = "http://localhost:8000"
NODE_B = "http://localhost:8001"

def test_p2p():
    print("--- DÉBUT DU TEST P2P ---")
    time.sleep(2) # Attendre que les serveurs démarrent

    # 1. Enregistrement des pairs
    print("[1/3] Enregistrement des pairs...")
    requests.post(f"{NODE_A}/api/p2p/peer?peer_url={NODE_B}")
    
    # 2. Test Propagation Transaction
    print("[2/3] Test propagation transaction...")
    tx = {
        "expediteur": "ALICE_PUB_KEY",
        "destinataire": "BOB_PUB_KEY",
        "donnees": "TX_DATA_123",
        "secteur": "PAIEMENT",
        "description": "Transfert test",
        "montant": 100,
        "horodatage": time.time(),
        "hash": "abc123hash"
    }
    resp = requests.post(f"{NODE_A}/api/p2p/transaction", json=tx)
    print(f"Transaction envoyée à A, réponse : {resp.json()}")

    # 3. Test Propagation Bloc
    print("[3/3] Test propagation bloc...")
    block = {
        "index": 1,
        "timestamp": time.time(),
        "transactions": [tx],
        "previous_hash": "0" * 64,
        "nonce": 12345,
        "merkle_root": "root123",
        "hash": "blockhash123"
    }
    # Ici, nous ne pouvons pas tester le "previous_hash" réel car les serveurs sont vides
    # mais nous testons la route d'API
    resp = requests.post(f"{NODE_A}/api/p2p/block", json=block)
    print(f"Bloc envoyé à A, réponse : {resp.json()}")

    print("--- FIN DU TEST ---")

if __name__ == "__main__":
    test_p2p()
