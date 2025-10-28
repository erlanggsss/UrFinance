import sqlite3
import os
from typing import Optional, Dict, Any
from src.analysis import analyze_invoices

def get_db_path():
    """Get the database path"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'database', 'invoices.db')

def get_db_connection():
    """Get database connection - supports both SQLite and Supabase"""
    try:
        from src.db_config import get_raw_connection
        return get_raw_connection()
    except ImportError:
        return sqlite3.connect(get_db_path())

def get_placeholder():
    """Get SQL parameter placeholder for current database"""
    try:
        from src.db_config import USE_SUPABASE
        return "%s" if USE_SUPABASE else "?"
    except ImportError:
        return "?"

def init_spending_limits_table():
    """Initialize the spending limits table in the database."""
    # Skip initialization for Supabase - table already exists from schema
    try:
        from src.db_config import USE_SUPABASE
        if USE_SUPABASE:
            print("ℹ️  Using Supabase - spending_limits table already exists")
            return  # Table already created in Supabase via create_schema.sql
    except ImportError:
        pass
    
    # Only initialize for SQLite
    print("ℹ️  Initializing spending_limits table for SQLite...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending_limits (
                user_id INTEGER PRIMARY KEY,
                monthly_limit REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def set_monthly_limit(user_id: int, limit_amount: float) -> bool:
    """Set or update monthly spending limit for a user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()
        
        # Use appropriate UPSERT syntax
        try:
            from src.db_config import USE_SUPABASE
            is_postgres = USE_SUPABASE
        except ImportError:
            is_postgres = False
        
        if is_postgres:
            cursor.execute(f'''
                INSERT INTO spending_limits (user_id, monthly_limit, updated_at)
                VALUES ({placeholder}, {placeholder}, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    monthly_limit = EXCLUDED.monthly_limit,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, limit_amount))
        else:
            cursor.execute(f'''
                INSERT INTO spending_limits (user_id, monthly_limit, updated_at)
                VALUES ({placeholder}, {placeholder}, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    monthly_limit = excluded.monthly_limit,
                    updated_at = CURRENT_TIMESTAMP
            ''', (user_id, limit_amount))
        
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_monthly_limit(user_id: int) -> Optional[float]:
    """Get the monthly spending limit for a user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        placeholder = get_placeholder()
        cursor.execute(f'SELECT monthly_limit FROM spending_limits WHERE user_id = {placeholder}', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_current_month_spending(user_id: int) -> float:
    """Get the total spending using the same calculation as view_summary."""
    try:
        analysis = analyze_invoices()
        return float(analysis['total_spent'])
    except Exception:
        return 0.0

def check_spending_limit(user_id: int, new_amount: float = 0) -> Dict[str, Any]:
    """Check if a new transaction would exceed the monthly spending limit."""
    monthly_limit = get_monthly_limit(user_id)
    if not monthly_limit:
        return {
            'has_limit': False,
            'message': 'No spending limit set. Use /set_limit to set one.'
        }

    current_spending = get_current_month_spending(user_id)
    # For new invoices being processed, add the new amount
    # For checking current status, new_amount will be 0
    total_with_new = current_spending + new_amount if new_amount > 0 else current_spending
    
    remaining = monthly_limit - current_spending
    percentage_used = (current_spending / monthly_limit) * 100  # Calculate percentage based on current spending

    message = (
        f"💰 Monthly Spending Status:\n\n"
        f"Monthly Limit: Rp {monthly_limit:,.2f}\n"
        f"Total Spent: Rp {current_spending:,.2f}\n"
    )

    if new_amount > 0:
        message += (
            f"\nAfter this transaction:\n"
            f"New Total: Rp {total_with_new:,.2f}\n"
        )

    message += (
        f"\nRemaining: Rp {remaining:,.2f}\n"
        f"Usage: {percentage_used:.1f}%"
    )

    return {
        'has_limit': True,
        'limit': monthly_limit,
        'current_spending': current_spending,
        'new_total': total_with_new,
        'remaining': remaining,
        'exceeds_limit': total_with_new > monthly_limit,
        'percentage_used': percentage_used,
        'message': message
    }