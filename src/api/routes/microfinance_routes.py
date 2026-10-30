from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.api.instances import blockchain_instance, microfinance_manager, foncier_uf, agriculture_manager, pending_land_requests, pending_diploma_requests
from src.utils.persistence import save_state

router = APIRouter()

class SendMoneyRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float
    description: str

@router.post("/send")
async def send_money(data: SendMoneyRequest):
    """Crée une demande d'envoi d'argent."""
    transfer = microfinance_manager.create_transfer_request(
        data.sender_id, data.receiver_id, data.amount, data.description
    )
    
    if not transfer:
        raise HTTPException(
            status_code=400, 
            detail="Solde insuffisant pour effectuer ce transfert."
        )
    
    save_state(
        blockchain_instance, 
        foncier_uf, 
        pending_land_requests, 
        agriculture_manager.lots, 
        pending_diploma_requests,
        microfinance_manager.pending_transfers
    )
    
    return {"status": "SUCCESS", "message": "Transfert en attente d'acceptation", "transfer": transfer}

@router.get("/pending/{user_id}")
async def get_pending_transfers(user_id: str):
    """Liste les transferts en attente pour un utilisateur."""
    return microfinance_manager.get_pending_for_user(user_id)

@router.post("/accept/{transfer_id}")
async def accept_transfer(transfer_id: int):
    """Le destinataire accepte le transfert."""
    transfer, error = microfinance_manager.accept_transfer(transfer_id)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    save_state(
        blockchain_instance, 
        foncier_uf, 
        pending_land_requests, 
        agriculture_manager.lots, 
        pending_diploma_requests,
        microfinance_manager.pending_transfers
    )
    
    return {"status": "SUCCESS", "message": "Argent reçu et validé sur blockchain", "transfer": transfer}
