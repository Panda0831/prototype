import pytest
from src.algorithms.union_find import UnionFind

def test_union_find_initialization():
    """Vérifie l'initialisation et l'ajout d'éléments."""
    uf = UnionFind()
    uf.add("Parcelle_A")
    uf.add("Proprietaire_1")
    
    assert uf.exists("Parcelle_A") is True
    assert uf.exists("Parcelle_B") is False
    assert uf.find("Parcelle_A") == "Parcelle_A"

def test_union_simple():
    """Vérifie la fusion de deux éléments (une vente)."""
    uf = UnionFind()
    uf.add("Parcelle_A")
    uf.add("Proprietaire_1")
    
    # Au début, ils sont séparés
    assert uf.is_connected("Parcelle_A", "Proprietaire_1") is False
    
    # On effectue la vente (union)
    success = uf.union("Parcelle_A", "Proprietaire_1")
    assert success is True
    
    # Maintenant ils sont connectés
    assert uf.is_connected("Parcelle_A", "Proprietaire_1") is True
    # Le propriétaire (root) doit être trouvé pour la parcelle
    assert uf.find("Parcelle_A") == uf.find("Proprietaire_1")

def test_union_multiple_parcelles():
    """Vérifie le regroupement de plusieurs parcelles sous un même propriétaire."""
    uf = UnionFind()
    parcelles = ["P1", "P2", "P3"]
    proprio = "Jean"
    
    uf.add(proprio)
    for p in parcelles:
        uf.add(p)
        uf.union(p, proprio)
    
    # Toutes les parcelles doivent avoir la même racine que Jean
    root = uf.find(proprio)
    for p in parcelles:
        assert uf.find(p) == root
    
    # P1 et P2 doivent être connectées car elles appartiennent au même ensemble
    assert uf.is_connected("P1", "P2") is True

def test_double_vente_detection():
    """Vérifie que l'union retourne False si deux éléments sont déjà connectés."""
    uf = UnionFind()
    uf.add("P1")
    uf.add("Jean")
    uf.add("Marc")
    
    # Jean achète P1
    uf.union("P1", "Jean")
    
    # On vérifie qu'ils ont la même racine
    assert uf.find("P1") == uf.find("Jean")
    
    # Une deuxième union entre P1 et Jean retournerait False car ils sont déjà connectés
    assert uf.union("P1", "Jean") is False

def test_path_compression_and_rank():
    """Vérifie indirectement l'efficacité (compression de chemin et rang)."""
    uf = UnionFind()
    elements = [f"E{i}" for i in range(10)]
    for e in elements:
        uf.add(e)
    
    # Création d'une chaîne
    for i in range(9):
        uf.union(elements[i], elements[i+1])
    
    root = uf.find("E0")
    # Après find("E0"), tous les éléments sur le chemin devraient pointer vers root
    for e in elements:
        assert uf.find(e) == root
