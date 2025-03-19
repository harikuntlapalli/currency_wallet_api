from app.config import Config

# Create database tables
def init_db():
    Config.Base.metadata.create_all(bind=Config.engine)

# Dependency for getting DB session
def get_db():
    db = Config.SessionLocal()
    try:
        yield db
    finally:
        db.close()
