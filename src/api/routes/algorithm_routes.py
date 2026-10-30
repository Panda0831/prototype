from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

from src.api.instances import graphe, brain
from src.algorithms.astar import AStar

router = APIRouter()

class PathRequest(BaseModel):
    start_id: int
    end_id: int

class ValidationRequest(BaseModel):
    current_district_id: int

@router.get("/districts")
async def get_districts():
    """Retourne la liste de tous les districts pour le frontend."""
    return [
        {"id": d.id, "nom": d.nom, "region": d.region, "lat": d.lat, "lon": d.lon}
        for d in graphe.districts.values()
    ]

@router.post("/path")
async def find_path(req: PathRequest):
    """
    Utilise l'algorithme A* pour trouver le chemin le plus court 
    de propagation d'un bloc entre deux districts.
    """
    solver = AStar(graphe)
    chemin_ids, distance = solver.chercher(req.start_id, req.end_id)
    
    if not chemin_ids:
        raise HTTPException(status_code=404, detail="Chemin non trouvé")
        
    chemin_details = []
    for d_id in chemin_ids:
        d = graphe.districts[d_id]
        chemin_details.append({"id": d.id, "nom": d.nom, "lat": d.lat, "lon": d.lon})
        
    return {
        "chemin": chemin_details,
        "distance_km": round(distance, 2)
    }

@router.post("/select-validator")
async def select_validator(req: ValidationRequest):
    """
    Utilise le Q-Learning pour choisir le meilleur district validateur 
    en fonction de l'état actuel (district d'origine de la transaction).
    """
    # Dans une démo, on simule une récompense basée sur la latence/énergie
    validator_id = brain.choisir_action(req.current_district_id)
    
    # Simulation d'apprentissage : on donne une bonne récompense si le validateur est proche
    d1 = graphe.districts[req.current_district_id]
    d2 = graphe.districts[validator_id]
    dist = graphe.calculer_distance_haversine(d1.lat, d1.lon, d2.lat, d2.lon)
    
    # Récompense inversement proportionnelle à la distance
    recompense = 100 / (dist + 1)
    brain.mettre_a_jour(req.current_district_id, validator_id, recompense, validator_id)
    
    return {
        "selected_validator": graphe.districts[validator_id].nom,
        "validator_id": validator_id,
        "reason": "Optimisation via Q-Learning (Énergie/Latence)",
        "score_q": brain.q_table[req.current_district_id][validator_id]
    }
