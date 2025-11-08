import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase: Client = None

def init_db(app):
    """Initialize Supabase database connection"""
    global supabase
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase database connected successfully!")
    
    return supabase

def get_supabase():
    """Get Supabase client instance"""
    if supabase is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return supabase

