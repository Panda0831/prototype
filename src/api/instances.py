# instances
from src.algorithms.qlearning import QLearningValidator
from src.algorithms.union_find import UnionFind
from src.blockchain.blockchain import Blockchain
from src.blockchain.peer_manager import PeerManager
from src.models.graph import DistrictsGraph
from src.use_cases.diploma import DiplomaManager
from src.use_cases.produitsAgricoles import AgricultureManager
from src.utils.persistence import load_state
import os

# Instance globale pour le stockage des notifications
notifications = []

# Simple tracking for demo
parcel_owner_map = {}

# Peer Manager pour la synchronisation décentralisée
NODE_ADDRESS = os.getenv("NODE_ADDRESS", "http://localhost:8000")
peer_manager = PeerManager(NODE_ADDRESS)

from src.blockchain.network_simulator import get_realistic_state

# ...

def get_network_state_id(district_id: int, pending_tx_count: int) -> int:
    """
    Utilise le simulateur réseau pour retourner un ID d'état réaliste pour l'IA.
    """
    return get_realistic_state(district_id, pending_tx_count)

# Chargement de l'état persisté
(
    blockchain_instance,
    foncier_uf,
    pending_land_requests,
    agri_lots,
    pending_diploma_requests,
    pending_transfers,
) = load_state()
# ... (rest of file)
# Initialisation par défaut si aucun état n'existe
if blockchain_instance is None:
    blockchain_instance = Blockchain()

if foncier_uf is None:
    foncier_uf = UnionFind()

# Instance globale pour le Graphe des districtsh
#
#
graphe = DistrictsGraph()
try:
    graphe.charger_depuis_csv("data/districts_madagascar.csv")
    graphe.generer_reseau_automatique(k=3)
except Exception as e:
    print(f"Erreur chargement graphe: {e}")

# Instance globale pour l'IA de validation
actions = list(graphe.districts.keys()) if graphe.districts else [1, 2, 3]
brain = QLearningValidator(actions_possibles=actions)
brain.charger_cerveau() # Charger les acquis sauvegardés

# Instance pour la gestion de l'Agriculture
agriculture_manager = AgricultureManager(blockchain_instance, graphe)
if agri_lots:
    agriculture_manager.lots = agri_lots

# Instance pour la gestion de l'Éducation
diploma_manager = DiplomaManager(blockchain_instance)

# Instance pour la Microfinance
from src.use_cases.microfinance import MicrofinanceManager

microfinance_manager = MicrofinanceManager(blockchain_instance)
if pending_transfers:
    microfinance_manager.pending_transfers = pending_transfers

# Synchronisation finale de l'état depuis la blockchain
from src.utils.sync import sync_all
all_instances = {
    "agriculture_manager": agriculture_manager,
    "foncier_uf": foncier_uf,
    "pending_land_requests": pending_land_requests,
    "diploma_manager": diploma_manager,
    "pending_diploma_requests": pending_diploma_requests,
    "microfinance_manager": microfinance_manager
}
sync_all(blockchain_instance, all_instances)
