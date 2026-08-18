"""
NEW FILE - does not modify any existing project files.

Creates the Supabase connection using environment variables:
  SUPABASE_URL
  SUPABASE_KEY   (service_role key, kept server-side only)

Set these in a local .env file for development, and in
Render -> your service -> Environment for deployment.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Missing SUPABASE_URL or SUPABASE_KEY environment variables. "
        "Add them to a .env file locally, or in Render's Environment tab."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
