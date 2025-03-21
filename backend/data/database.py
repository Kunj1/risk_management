# database.py
import os
from supabase import create_client, Client

# Singleton to maintain a single database connection
_db_client = None

def get_db_client() -> Client:
    """Get or create a Supabase client"""
    global _db_client
    
    if _db_client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
        
        _db_client = create_client(supabase_url, supabase_key)
    
    return _db_client

def initialize_db():
    """Initialize the database with required tables (if they don't exist)"""
    client = get_db_client()
    
    # In Supabase, we typically create tables via the web interface
    # or using migrations. This is a placeholder for that process.
    
    # Check if initialization is needed by querying for the projects table
    try:
        client.table("projects").select("count").limit(1).execute()
        print("Database tables already exist.")
    except Exception as e:
        print(f"Database initialization needed: {e}")
        
        # In a real application, you would either:
        # 1. Create tables via SQL here
        # 2. Use a migration system
        # 3. Redirect users to create tables in Supabase dashboard
        
        print("Please create required tables in Supabase dashboard.")