import pytest
from src.models.heap import TasBinaire

def test_insertion_et_extraction_min():
    """Vérifie que le tas retourne toujours l'élément avec la priorité la plus basse."""
    tas = TasBinaire()
    tas.inserer("District A", 10)
    tas.inserer("District B", 5)
    tas.inserer("District C", 20)
    tas.inserer("District D", 1)

    assert tas.extraire_min() == (1, "District D")
    assert tas.extraire_min() == (5, "District B")
    assert tas.extraire_min() == (10, "District A")
    assert tas.extraire_min() == (20, "District C")
    assert tas.est_vide() is True

def test_tas_vide():
    """Vérifie le comportement avec un tas vide."""
    tas = TasBinaire()
    assert tas.extraire_min() is None
    assert tas.est_vide() is True

def test_ordre_aleatoire():
    """Vérifie l'ordre avec plusieurs insertions désordonnées."""
    tas = TasBinaire()
    priorites = [42, 12, 88, 5, 23]
    for p in priorites:
        tas.inserer(f"Val_{p}", p)

    resultats = []
    while not tas.est_vide():
        resultats.append(tas.extraire_min()[0])

    assert resultats == sorted(priorites)
