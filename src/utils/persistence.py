import json
import os
import pickle
from src.blockchain.blockchain import Blockchain
from src.algorithms.union_find import UnionFind

DATA_DIR = "data/persistence"

def save_state(blockchain, foncier_uf, pending_requests, agri_lots=None, pending_diploma_requests=None, pending_transfers=None):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    with open(os.path.join(DATA_DIR, "blockchain.pkl"), "wb") as f:
        pickle.dump(blockchain, f)
    
    with open(os.path.join(DATA_DIR, "foncier_uf.pkl"), "wb") as f:
        pickle.dump(foncier_uf, f)
        
    with open(os.path.join(DATA_DIR, "pending_requests.json"), "w") as f:
        json.dump(pending_requests, f)
    
    if pending_diploma_requests is not None:
        with open(os.path.join(DATA_DIR, "pending_diploma_requests.json"), "w") as f:
            json.dump(pending_diploma_requests, f)

    if pending_transfers is not None:
        with open(os.path.join(DATA_DIR, "pending_transfers.json"), "w") as f:
            json.dump(pending_transfers, f)
    
    if agri_lots is not None:
        with open(os.path.join(DATA_DIR, "agri_lots.pkl"), "wb") as f:
            pickle.dump(agri_lots, f)

def load_state():
    blockchain = None
    foncier_uf = None
    pending_requests = []
    pending_diploma_requests = []
    pending_transfers = []
    agri_lots = {}
    
    bc_path = os.path.join(DATA_DIR, "blockchain.pkl")
    uf_path = os.path.join(DATA_DIR, "foncier_uf.pkl")
    pr_path = os.path.join(DATA_DIR, "pending_requests.json")
    pdr_path = os.path.join(DATA_DIR, "pending_diploma_requests.json")
    pt_path = os.path.join(DATA_DIR, "pending_transfers.json")
    ag_path = os.path.join(DATA_DIR, "agri_lots.pkl")
    
    if os.path.exists(bc_path):
        with open(bc_path, "rb") as f:
            blockchain = pickle.load(f)
            
    if os.path.exists(uf_path):
        with open(uf_path, "rb") as f:
            foncier_uf = pickle.load(f)
            
    if os.path.exists(pr_path):
        with open(pr_path, "r") as f:
            pending_requests = json.load(f)

    if os.path.exists(pdr_path):
        with open(pdr_path, "r") as f:
            pending_diploma_requests = json.load(f)

    if os.path.exists(pt_path):
        with open(pt_path, "r") as f:
            pending_transfers = json.load(f)

    if os.path.exists(ag_path):
        with open(ag_path, "rb") as f:
            agri_lots = pickle.load(f)
            
    return blockchain, foncier_uf, pending_requests, agri_lots, pending_diploma_requests, pending_transfers
