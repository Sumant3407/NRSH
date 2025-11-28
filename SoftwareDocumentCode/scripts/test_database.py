"""
Test script to verify Supabase database connection
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.database_service import get_database_service


def test_connection():
    """Test Supabase database connection"""
    print("Testing Supabase database connection...")
    print("-" * 50)
    
    try:
        db_service = get_database_service()
        
        if db_service is None:
            print("❌ Database service not initialized")
            print("\nPossible reasons:")
            print("1. SUPABASE_URL not set in .env file")
            print("2. SUPABASE_KEY not set in .env file")
            print("3. Invalid credentials")
            print("\nThe system will use file-based storage as fallback.")
            return False
        
        print("✅ Database service initialized successfully")
        
        # Test a simple query
        try:
            videos = db_service.client.table("videos").select("id").limit(1).execute()
            print("✅ Database connection verified")
            print(f"✅ Tables accessible (found {len(videos.data)} test records)")
            return True
        except Exception as e:
            print(f"⚠️  Connection verified but query failed: {e}")
            print("   This might mean tables don't exist yet.")
            print("   Run database/schema.sql in Supabase SQL Editor")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check SUPABASE_URL and SUPABASE_KEY in .env")
        print("2. Verify Supabase project is active")
        print("3. Check network connection")
        return False


if __name__ == "__main__":
    success = test_connection()
    print("-" * 50)
    if success:
        print("✅ Database setup is complete!")
    else:
        print("⚠️  Database setup incomplete. System will use file-based storage.")
    sys.exit(0 if success else 1)

