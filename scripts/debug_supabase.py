import os
import traceback

from dotenv import load_dotenv

load_dotenv()
print("SUPABASE_URL=", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY=", "SET" if os.getenv("SUPABASE_KEY") else "NOT SET")

try:
    from supabase import create_client

    print("create_client imported")
    client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    print("client created:", type(client))
except Exception as e:
    print("Exception during create_client:")
    traceback.print_exc()
