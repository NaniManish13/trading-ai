"""
Database connection and session management
"""
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import DATABASE_URL, DB_PATH
from database.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine with SQLite-specific configuration
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database with all tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✓ Database initialized at {DB_PATH}")
        logger.info(f"✓ Tables created: {tables}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise


def get_session() -> Session:
    """Create and return a new database session"""
    return SessionLocal()


def close_db():
    """Close the database connection"""
    engine.dispose()


# Initialize database on import
if __name__ != "__main__":
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database initialization on import: {e}")
