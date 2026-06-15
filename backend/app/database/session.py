from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sqlalchemy.orm import sessionmaker, DeclarativeBase 


load_dotenv()

class Base(DeclarativeBase):
    pass



POSTGRES_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5435/{os.getenv('DB_NAME')}"
engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "123456789")
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_neo4j_driver():
    try:
        yield neo4j_driver
    finally:
        pass