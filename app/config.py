from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Config:
    # API Configuration
    NBP_API_URL = "https://api.nbp.pl/api/exchangerates/rates/C/"
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    TOKEN_EXPIRATION = 3600

    # Database Configuration
    DATABASE_URL = "sqlite:///./wallet.db"

    # Create database engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base model for SQLAlchemy
    Base = declarative_base()
