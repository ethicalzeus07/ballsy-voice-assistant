"""
Database layer using SQLAlchemy for PostgreSQL/Cloud SQL compatibility.
Supports both SQLite (local dev) and PostgreSQL (production).
"""

import logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from contextlib import contextmanager
from typing import Generator
from src.backend.config import config

logger = logging.getLogger(__name__)

Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", backref="conversations")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    is_user = Column(Boolean, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    
    conversation = relationship("Conversation", backref="messages")


class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    voice = Column(String, default="Daniel")
    voice_speed = Column(Integer, default=180)
    theme = Column(String, default="light")
    
    user = relationship("User", backref="settings")


class CommandHistory(Base):
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    command = Column(Text, nullable=False)
    result = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
    
    user = relationship("User", backref="command_history")


# Database engine and session - lazy initialization
_engine = None
_SessionLocal = None
_initialized = False


def _get_db_url():
    """Get the database URL, ensuring psycopg2 driver for PostgreSQL."""
    if config.DATABASE_URL.startswith("postgresql"):
        # Ensure we're using psycopg2 driver
        if "psycopg2" not in config.DATABASE_URL:
            # Replace postgresql:// with postgresql+psycopg2://
            return config.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    return config.DATABASE_URL


def _get_engine():
    """Lazy initialization of database engine."""
    global _engine
    if _engine is None:
        db_url = _get_db_url()
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL debugging
            connect_args={"connect_timeout": 5}  # 5 second timeout
        )
    return _engine


def _get_session_factory():
    """Lazy initialization of session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    return _SessionLocal


def init_database(retry: bool = True, max_retries: int = 3, delay: float = 2.0):
    """
    Initialize database connection and create tables.
    Uses retry logic to handle Cloud SQL not being ready.
    """
    global _initialized
    
    if _initialized:
        return True
    
    import time
    from sqlalchemy.exc import OperationalError
    
    for attempt in range(max_retries if retry else 1):
        try:
            engine = _get_engine()
            
            # Test connection
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()  # Actually execute the query
            
            # Create session factory
            _get_session_factory()
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            
            _initialized = True
            logger.info(f"Database initialized: {config.DATABASE_URL.split('@')[-1] if '@' in config.DATABASE_URL else 'local'}")
            return True
            
        except (OperationalError, Exception) as e:
            if attempt < max_retries - 1 and retry:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to initialize database after {attempt + 1} attempts: {e}", exc_info=True)
                if not retry:
                    raise
                # Don't raise - allow app to start without DB
                return False
    
    return False


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions. Lazy-initializes if needed."""
    # Try to initialize if not already done
    if not _initialized:
        init_database(retry=True, max_retries=1, delay=1.0)
    
    SessionLocal = _get_session_factory()
    if SessionLocal is None:
        raise RuntimeError("Database not available. Check connection and retry.")
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_db_connection(max_retries: int = 3, delay: float = 1.0) -> bool:
    """Check if database is reachable. Returns True if connection succeeds."""
    import time
    from sqlalchemy.exc import OperationalError
    from sqlalchemy import text
    
    try:
        engine = _get_engine()
        for attempt in range(max_retries):
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True
            except OperationalError as e:
                if attempt < max_retries - 1:
                    logger.debug(f"DB check attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay)
                else:
                    logger.warning(f"DB connection check failed after {max_retries} attempts: {e}")
                    return False
    except Exception as e:
        logger.error(f"DB connection check error: {e}")
        return False
    
    return False


def clear_conversation_history():
    """Clear all conversation history for a fresh start."""
    try:
        with get_db_session() as session:
            session.query(Message).delete()
            session.query(CommandHistory).delete()
            session.query(Conversation).delete()
            session.commit()
            logger.info("✨ Conversation history cleared - Fresh start for Ballsy!")
    except Exception as e:
        logger.error(f"Error clearing history: {e}")

