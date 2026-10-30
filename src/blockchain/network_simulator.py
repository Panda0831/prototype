import random

def simulate_network_metrics(district_id):
    """
    Simule des données réalistes pour un district.
    """
    # Énergie: 0-100 (le district d'Antananarivo (ID 1) est stable, d'autres varient)
    energy = 90 if district_id == 1 else random.randint(20, 95)
    # Vitesse de connexion (Mbps)
    speed = 100 if district_id == 1 else random.randint(5, 110)
    # Charge CPU du nœud (0-100)
    load = random.randint(10, 90)
    
    return {"energy": energy, "speed": speed, "load": load}

def get_realistic_state(district_id, pending_tx_count):
    """
    Calcule un état complexe basé sur les métriques réelles.
    0: Optimal, 1: Dégradé, 2: Critique
    """
    metrics = simulate_network_metrics(district_id)
    
    # Logique métier: Si énergie < 30 ou charge > 80 ou vitesse < 10 -> Critique (2)
    if metrics["energy"] < 30 or metrics["load"] > 80 or metrics["speed"] < 10:
        return 2
    # Si charge modérée ou vitesse moyenne -> Dégradé (1)
    elif metrics["load"] > 50 or metrics["speed"] < 50:
        return 1
    # Sinon -> Optimal (0)
    return 0
