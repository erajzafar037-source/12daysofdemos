import os
import time
import pandas as pd
from psycopg import sql
from psycopg_pool import ConnectionPool
from databricks import sdk

# Global connection pool
connection_pool = None
postgres_password = None
last_password_refresh = 0
workspace_client = sdk.WorkspaceClient()

def _refresh_token():
    """Internal helper to handle OAuth tokens."""
    global postgres_password, last_password_refresh
    if postgres_password is None or time.time() - last_password_refresh > 900:
        try:
            postgres_password = workspace_client.config.oauth_token().access_token
            last_password_refresh = time.time()
        except Exception as e:
            print(f"❌ Token Refresh Error: {e}")
            raise e

def _get_pool():
    """Ensures a valid connection pool exists."""
    global connection_pool
    if connection_pool is None:
        _refresh_token()
        conn_string = (
            f"dbname={os.getenv('PGDATABASE')} user={os.getenv('PGUSER')} "
            f"password={postgres_password} host={os.getenv('PGHOST')} "
            f"port={os.getenv('PGPORT')} sslmode={os.getenv('PGSSLMODE', 'require')}"
        )
        connection_pool = ConnectionPool(conn_string, min_size=2, max_size=10)
    return connection_pool

def fetch_data():
    """Returns the dataframe from the database."""
    try:
        pool = _get_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM public.gift_requests_synced_table")
                rows = cur.fetchall()
                if cur.description:
                    cols = [desc[0] for desc in cur.description]
                    return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        print(f"Query Error: {e}")
        # Return empty structure if DB fails
        return pd.DataFrame(columns=[
            'request_id', 'timestamp', 'child_id', 'latitude', 'longitude', 
            'country', 'primary_gift_category', 'gift_count',
            'delivery_preference', 'en_route', 'delivered', 'cookies'
        ])

def update_db_record(request_id, column, value):
    """Updates a single cell in the database."""
    # Sanitization
    if column in ['en_route', 'delivered']: value = bool(value)
    if column == 'cookies': value = int(value) if value is not None else 0
    
    query = sql.SQL("UPDATE public.gift_requests_synced_table SET {} = %s WHERE request_id = %s").format(sql.Identifier(column))
    
    try:
        pool = _get_pool()
        with pool.connection() as conn:
            conn.execute(query, (value, request_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False