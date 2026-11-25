from backend.database.session import Base, engine
import backend.models.models  # Register models

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully!")
