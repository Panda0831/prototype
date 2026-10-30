import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """
    Représente un utilisateur ou une entité (Acteur) dans la base de données.
    Synchronisé avec le modèle métier Acteur.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # ex: UNIVERSITE, RECOLTEUR
    district = Column(String)  # ex: Antalaha, Toliara
    public_key = Column(String, unique=True)

    # Relations ORM
    transactions_envoyees = relationship(
        "Transaction", foreign_keys="Transaction.expediteur_id", back_populates="expediteur"
    )
    transactions_recues = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="destinataire",
    )


class Transaction(Base):
    """
    Stockage persistant de chaque transaction validée sur la blockchain.
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String, unique=True, index=True)

    # Liens vers les utilisateurs (Foreign Keys)
    expediteur_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))

    # Détails de la transaction
    secteur = Column(String)  # VANILLE, DIPLOME, FONCIER, etc.
    description = Column(String)
    donnees = Column(Text)  # Données au format JSON/Texte
    montant = Column(Float, default=0.0)

    # Preuves cryptographiques
    signature = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Appartenance à un bloc
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)

    # Relations ORM
    expediteur = relationship(
        "User", foreign_keys=[expediteur_id], back_populates="transactions_envoyees"
    )
    destinataire = relationship(
        "User", foreign_keys=[receiver_id], back_populates="transactions_recues"
    )
    bloc = relationship("Block", back_populates="transactions")


class Block(Base):
    """
    Représente un bloc immuable de la blockchain.
    """

    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    index = Column(Integer, unique=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    prev_hash = Column(String)
    hash = Column(String, unique=True)
    merkle_root = Column(String)
    nonce = Column(Integer, default=0)  # number used once

    # Un bloc contient une liste de transactions
    transactions = relationship("Transaction", back_populates="bloc")
