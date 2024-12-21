import sqlalchemy as sa
import config

def connect() -> sa.engine.Connection:
    engine = sa.create_engine(config.get_db_url())
    return engine.connect()

def disconnect(conn: sa.engine.Connection):
    conn.close()