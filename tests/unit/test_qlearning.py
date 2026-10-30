import pytest
import os
from src.algorithms.qlearning import QLearningValidator

def test_qlearning_learning_convergence():
    """Vérifie que l'agent apprend à choisir l'action qui donne la meilleure récompense."""
    actions = [1, 2, 3]
    agent = QLearningValidator(actions_possibles=actions, epsilon=0.1)
    
    etat = 1
    # On veut que l'agent apprenne que l'action '2' est la meilleure pour l'état '1'
    meilleure_action = 2
    
    # Entraînement sur 200 itérations
    for _ in range(200):
        action = agent.choisir_action(etat)
        recompense = 10.0 if action == meilleure_action else -1.0
        agent.mettre_a_jour(etat, action, recompense, prochain_etat=etat)
    
    # Après l'entraînement, on réduit epsilon à 0 (exploitation pure)
    agent.epsilon = 0
    choix_final = agent.choisir_action(etat)
    
    assert choix_final == meilleure_action
    assert agent.q_table[etat][meilleure_action] > agent.q_table[etat][1]

def test_save_and_load_brain():
    """Vérifie que la sauvegarde et le chargement de la Q-Table fonctionnent."""
    path = "tests/unit/test_q_table.json"
    agent = QLearningValidator(actions_possibles=[1, 2])
    agent.q_table = {1: {1: 0.5, 2: 0.8}}
    
    agent.sauvegarder_cerveau(path)
    
    nouveau_agent = QLearningValidator(actions_possibles=[1, 2])
    nouveau_agent.charger_cerveau(path)
    
    assert nouveau_agent.q_table[1][2] == 0.8
    
    # Nettoyage
    if os.path.exists(path):
        os.remove(path)
