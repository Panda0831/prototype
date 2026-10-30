from fastapi import APIRouter, HTTPException
from src.api.instances import peer_manager, blockchain_instance
from src.blockchain.transaction import Transaction
from src.blockchain.block import Block

router = APIRouter()

@router.post("/peer")
async def add_peer(peer_url: str):
    """Enregistre un nouveau pair."""
    peer_manager.add_peer(peer_url)
    return {"message": "Peer ajouté avec succès", "peers": peer_manager.get_peers()}

@router.get("/peers")
async def get_peers():
    """Liste tous les pairs connus."""
    return {"peers": peer_manager.get_peers()}

@router.post("/transaction")
async def receive_transaction(transaction_data: dict):
    """Reçoit une transaction propagée par un pair."""
    try:
        tx = Transaction.from_dict(transaction_data)
        if blockchain_instance.ajouter_transaction(tx):
            return {"status": "success", "message": "Transaction added"}
        else:
            raise HTTPException(status_code=400, detail="Invalid transaction")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/block")
async def receive_block(block_data: dict):
    """Reçoit un bloc propagé par un pair."""
    try:
        new_block = Block.from_dict(block_data)
        
        # Validation basique : le précédent hash doit correspondre
        last_block = blockchain_instance.obtenir_dernier_bloc()
        if new_block.previous_hash != last_block.hash:
            raise HTTPException(status_code=400, detail="Block previous hash mismatch")
            
        # Validation de l'index
        if new_block.index != last_block.index + 1:
            raise HTTPException(status_code=400, detail="Invalid block index")
            
        # Ajouter le bloc
        blockchain_instance.chaine.append(new_block)
        # Vider les transactions en attente qui ont été incluses dans ce bloc
        blockchain_instance.transactions_en_attente = [] 
        
        return {"status": "success", "message": "Block added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
