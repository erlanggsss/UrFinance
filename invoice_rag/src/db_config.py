"""
Unified Database Configuration Module
Supports both SQLite (local) and PostgreSQL/Supabase (cloud)
Switch between databases using USE_SUPABASE environment variable
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database selection flag
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

def get_database_url():
    """
    Get appropriate database URL based on configuration.
    Returns SQLite or PostgreSQL connection string.
    """
    if USE_SUPABASE:
        # PostgreSQL/Supabase connection
        db_host = os.getenv("SUPABASE_DB_HOST")
        db_port = os.getenv("SUPABASE_DB_PORT", "5432")
        db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
        db_user = os.getenv("SUPABASE_DB_USER", "postgres")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        if not all([db_host, db_password]):
            raise ValueError(
                "Missing Supabase credentials. Required: "
                "SUPABASE_DB_HOST, SUPABASE_DB_PASSWORD"
            )
        
        # PostgreSQL connection string
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # SQLite connection (legacy)
        from src.database import get_default_db_path
        db_path = get_default_db_path()
        return f"sqlite:///{db_path}"

def get_engine():
    """
    Create SQLAlchemy engine based on database type.
    Includes connection pooling for PostgreSQL.
    """
    db_url = get_database_url()
    
    if USE_SUPABASE:
        # PostgreSQL-specific settings
        # Increased pool size for production deployment on Railway
        return create_engine(
            db_url,
            pool_size=20,         # Increased from 5 to 20
            max_overflow=30,      # Increased from 10 to 30
            pool_pre_ping=True,   # Verify connections before use
            pool_timeout=30,      # Wait up to 30s for connection
            pool_recycle=3600,    # Recycle connections after 1 hour
            echo=False            # Set True for SQL debugging
        )
    else:
        # SQLite-specific settings
        return create_engine(
            db_url,
            connect_args={'check_same_thread': False},  # SQLite threading
            echo=False
        )

# Create scoped session factory for thread-safe session management
from contextlib import contextmanager

@contextmanager
def get_session():
    """
    Context manager for database sessions.
    Automatically handles session cleanup and ensures connections are returned to pool.
    
    Usage:
        with get_session() as session:
            user = session.query(User).first()
            # session automatically closed after this block
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_raw_connection():
    """
    Get raw database connection for modules using sqlite3 directly.
    Returns appropriate connection object (sqlite3 or psycopg2).
    """
    if USE_SUPABASE:
        import psycopg2
        db_host = os.getenv("SUPABASE_DB_HOST")
        db_port = os.getenv("SUPABASE_DB_PORT", "5432")
        db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
        db_user = os.getenv("SUPABASE_DB_USER", "postgres")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        return psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
    else:
        import sqlite3
        from src.database import get_default_db_path
        return sqlite3.connect(get_default_db_path())

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Execute raw SQL query with automatic dialect handling.
    Handles parameter placeholders (? for SQLite, %s for PostgreSQL).
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
        fetch_one: Return single row
        fetch_all: Return all rows (default)
    
    Returns:
        Query results or None for INSERT/UPDATE/DELETE
    """
    conn = get_raw_connection()
    cursor = conn.cursor()
    
    try:
        # Convert SQLite placeholders (?) to PostgreSQL (%s) if needed
        if USE_SUPABASE and '?' in query:
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        
        conn.commit()
        return result
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        cursor.close()
        conn.close()

# Convenience functions for common operations
def get_db_type():
    """Return current database type: 'sqlite' or 'postgresql'"""
    return "postgresql" if USE_SUPABASE else "sqlite"

def is_supabase():
    """Check if using Supabase"""
    return USE_SUPABASE

def get_placeholder():
    """Get SQL parameter placeholder for current database"""
    return "%s" if USE_SUPABASE else "?"

# Migration helper
def print_db_info():
    """Print current database configuration (for debugging)"""
    print(f"Database Type: {get_db_type()}")
    print(f"Connection: {get_database_url()}")
