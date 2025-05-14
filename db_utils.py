"""
Database utility functions for transaction management and error handling
"""
from functools import wraps
from db_init import get_db_connection
import traceback

def with_transaction(func):
    """Decorator for functions that need transaction management"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        try:
            result = func(*args, **kwargs, conn=conn)
            conn.commit()
            return result
        except Exception as e:
            print(f"Database error in {func.__name__}: {e}")
            traceback.print_exc()
            try:
                conn.rollback()
            except:
                pass  # Connection might already be closed
            return None
    return wrapper

def get_count(table_name, where_clause=None, params=None):
    """
    Get count from a table with optional where clause
    Example: get_count('users', 'role = :role', {'role': 'admin'})
    """
    conn = get_db_connection()
    try:
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        from sqlalchemy.sql import text
        result = conn.execute(text(query), params or {}).fetchone()
        
        # Handle different result types
        if result:
            try:
                if hasattr(result, "_mapping"):
                    return result._mapping[0] if 0 in result._mapping else result._mapping["count"]
                else:
                    return result[0]
            except Exception as e:
                print(f"Error accessing count: {e}")
        return 0
    except Exception as e:
        print(f"Error getting count from {table_name}: {e}")
        try:
            conn.rollback()
        except:
            pass
        return 0

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query with robust error handling
    
    Args:
        query: SQL query string
        params: Dictionary of query parameters
        fetch_one: Whether to fetch one result
        fetch_all: Whether to fetch all results
    
    Returns:
        Result of query, or None on error
    """
    conn = get_db_connection()
    try:
        from sqlalchemy.sql import text
        result = conn.execute(text(query), params or {})
        
        if fetch_one:
            return result.fetchone()
        elif fetch_all:
            return result.fetchall()
        else:
            conn.commit()
            return result
    except Exception as e:
        print(f"Error executing query: {e}")
        print(f"Query was: {query}")
        print(f"Params were: {params}")
        try:
            conn.rollback()
        except:
            pass
        return None 