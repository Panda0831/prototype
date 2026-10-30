from fastapi import APIRouter
from src.api.instances import notifications

router = APIRouter()

@router.get("/{public_key}")
async def get_notifications(public_key: str):
    """Récupère les notifications pour un utilisateur."""
    return [n for n in notifications if n["public_key"] == public_key]

@router.post("/add")
async def add_notification(data: dict):
    """Ajoute une notification (utilisé par les autres modules)."""
    notifications.append({
        "public_key": data["public_key"],
        "message": data["message"],
        "timestamp": data.get("timestamp", None)
    })
    return {"status": "SUCCESS"}
