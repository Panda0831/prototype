import json
import os
import random
from typing import Dict, List, Optional, Tuple


class QLearningValidator:
    """
    Agent d'apprentissage par renforcement (Q-Learning) pour optimiser
    la sélection des validateurs dans le réseau Hazo Lova.
    """

    def __init__(
        self,
        actions_possibles: List[int],
        # hyperparametres
        alpha: float = 0.1,  #  taux d'apprentissage
        gamma: float = 0.9,  #  facteur deremise
        epsilon: float = 0.1,  #  taux d'exploration
    ):
        """
        Initialise l'agent de Q-Learning.

        :param actions_possibles: Liste des IDs des districts pouvant être validateurs.
        :param alpha: Taux d'apprentissage (0 < alpha <= 1).
        :param gamma: Facteur de remise (importance des récompenses futures).
        :param epsilon: Taux d'exploration (probabilité de choisir une action au hasard).
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.actions = actions_possibles

        # Table Q : { etat_id: { action_id: valeur_q } }
        self.q_table: Dict[int, Dict[int, float]] = {}

    def _initialiser_etat(self, etat: int) -> None:
        """Initialise une ligne de la Q-Table si elle n'existe pas encore."""
        if etat not in self.q_table:
            self.q_table[etat] = {action: 0.0 for action in self.actions}

    def choisir_action(self, etat: int) -> int:
        """
        Sélectionne un validateur en utilisant la stratégie Epsilon-Greedy.
        """
        self._initialiser_etat(etat)

        # Exploration : choisir une action au hasard
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Exploitation : choisir la meilleure action connue (valeur Q max)
        return max(self.q_table[etat], key=lambda a: self.q_table[etat][a])

    def mettre_a_jour(
        self, etat: int, action: int, recompense: float, prochain_etat: int
    ) -> None:
        """
        Met à jour la Q-Table selon l'équation de Bellman.
        Q(s, a) = Q(s, a) + alpha * [recompense + gamma * max(Q(s', a')) - Q(s, a)]
        """
        # s : état actuel
        # a : action effectuée
        # r : récompense reçue
        # s' : nouvel état atteint
        # α (alpha) : taux d'apprentissage
        # γ (gamma) : facteur d'actualisation du futur
        # Q(s,a) : qualité estimée de l'action a dans l'état s
        self._initialiser_etat(etat)
        self._initialiser_etat(prochain_etat)

        max_q_prochain = max(self.q_table[prochain_etat].values())

        # Calcul du nouveau score Q
        valeur_actuelle = self.q_table[etat][action]
        nouvelle_valeur = valeur_actuelle + self.alpha * (
            recompense + self.gamma * max_q_prochain - valeur_actuelle
        )

        self.q_table[etat][action] = nouvelle_valeur

    def sauvegarder_cerveau(self, chemin: str = "data/q_table.json") -> None:
        """Persiste l'apprentissage dans un fichier JSON."""
        # Conversion des clés int en str pour JSON
        data_to_save = {str(k): v for k, v in self.q_table.items()}
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        try:
            with open(chemin, "w") as f:
                json.dump(data_to_save, f, indent=4)
            print(f" [!] Cerveau sauvegardé avec succès dans {chemin}")
        except Exception as e:
            print(f" [!] Erreur lors de la sauvegarde du cerveau: {e}")

    def charger_cerveau(self, chemin: str = "data/q_table.json") -> None:
        """Charge un apprentissage précédent."""
        if os.path.exists(chemin):
            with open(chemin, "r") as f:
                data = json.load(f)
                # Reconversion des clés str en int
                self.q_table = {
                    int(k): {int(ak): av for ak, av in v.items()}
                    for k, v in data.items()
                }

    def __repr__(self) -> str:
        return f"QLearningValidator(Etats connus: {len(self.q_table)})"
