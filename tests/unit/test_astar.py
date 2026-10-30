import pytest
from src.models.graph import DistrictsGraph
from src.algorithms.astar import AStar

def test_astar_madagascar_path():
    """Vérifie que A* trouve un chemin cohérent entre Tana et Tuléar."""
    g = DistrictsGraph()
    g.charger_depuis_csv("data/districts_madagascar.csv")
    
    # On génère un réseau où chaque district est lié à ses 5 voisins les plus proches
    g.generer_reseau_automatique(k=5)
    
    astar = AStar(g)
    
    # Antananarivo Renivohitra (ID 7) vers Toliara I (ID 113)
    chemin, distance = astar.chercher(7, 113)
    
    assert chemin is not None
    assert len(chemin) > 2
    assert distance > 500 # Tana-Tuléar fait environ 600-900 km selon les routes
    
    # Vérifier que le premier et le dernier sont corrects
    assert chemin[0] == 7
    assert chemin[-1] == 113
    
    print(f"\n Chemin trouvé ({len(chemin)} étapes, {distance:.2f} km) :")
    noms = [g.districts[cid].nom for cid in chemin]
    print(" -> ".join(noms))

def test_astar_aucun_chemin():
    """Vérifie le comportement si aucun chemin n'est possible."""
    g = DistrictsGraph()
    # On ajoute juste 2 districts isolés
    from src.models.graph import District
    g.districts[1] = District(1, "D1", "R1", -18, 47)
    g.districts[2] = District(2, "D2", "R1", -20, 48)
    # Pas de connexion ajoutée
    
    astar = AStar(g)
    chemin, distance = astar.chercher(1, 2)
    assert chemin is None
    assert distance == 0
