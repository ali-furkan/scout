from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import engine, create_engine
from config import Config

def create_db_engine() -> engine.Engine:
    return create_engine(Config.get_db_url())

def connect_engine(e: engine.Engine) -> engine.Connection:
    return e.connect()

def create_session(conn: engine.Connection) -> Session:
    Session = sessionmaker(bind=conn)
    return Session()

def disconnect(s: Session) -> bool:
    s.close()