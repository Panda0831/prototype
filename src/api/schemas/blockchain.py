from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum

class SecteurActivite(str, Enum):
    PRODUITS_AGRICOLES = "PRODUITS_AGRICOLES"
    DIPLOME = "DIPLOME"
    FONCIER = "FONCIER"
    MICROFINANCE = "MICROFINANCE"
    PAIEMENT = "PAIEMENT"

class TransactionCreate(BaseModel):
    expediteur: str = Field(..., description="Clé publique de l'expéditeur (Hex)")
    destinataire: str = Field(..., description="Clé publique du destinataire (Hex)")
    donnees: Any = Field(..., description="Données spécifiques au métier (ex: ID parcelle)")
    secteur: SecteurActivite
    description: Optional[str] = ""
    montant: Optional[float] = 0.0
    signature: str = Field(..., description="Signature de la transaction générée avec la clé privée")

class TransactionResponse(BaseModel):
    expediteur: str
    destinataire: str
    donnees: Any
    secteur: str
    description: str
    montant: float
    horodatage: float
    hash: str
    signature: Optional[str]

class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[TransactionResponse]
    previous_hash: str
    merkle_root: Optional[str]
    nonce: int
    hash: str

class BlockchainSummary(BaseModel):
    longueur: int
    dernier_hash: str
    est_valide: bool
