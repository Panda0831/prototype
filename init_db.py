from src.db.session import engine
from src.db.base import Base
from src.db.models import User, Transaction, Block

def init_db():
    print("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")

if __name__ == "__main__":
    init_db()
