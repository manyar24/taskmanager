from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

class Base(DeclarativeBase):
    pass

engine = None
SessionLocal = None

def init_db(database_url: str):
    global engine, SessionLocal
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
    SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))
    return engine

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database has not been initialized")
    return SessionLocal()

def close_db(_exc=None):
    if SessionLocal is not None:
        SessionLocal.remove()
