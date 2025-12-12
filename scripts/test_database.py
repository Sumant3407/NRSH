import sys
from pathlib import Path

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent

if project_root.name == "SoftwareDocumentCode":
    project_root = project_root.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.database_service import get_database_service


# Function: test_connection
def test_connection():
    """Test Supabase database connection"""
    print("Testing Supabase database connection...")
    print("-" * 50)

    try:
        db_service = get_database_service()
        assert db_service is not None, (
            "Database service not initialized. Possible reasons: 1) SUPABASE_URL not set, "
            "2) SUPABASE_KEY not set, 3) Invalid credentials. The system will use file-based storage as fallback."
        )

        print("✅ Database service initialized successfully")

        try:
            videos = db_service.client.table("videos").select("id").limit(1).execute()
            print("✅ Database connection verified")
            print(f"✅ Tables accessible (found {len(videos.data)} test records)")
            assert True
        except Exception as e:
            raise AssertionError(
                f"Connection verified but query failed: {e}. This might mean tables don't exist yet. "
                "Run database/schema.sql in Supabase SQL Editor"
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check SUPABASE_URL and SUPABASE_KEY in .env")
        print("2. Verify Supabase project is active")
        print("3. Check network connection")
        raise


if __name__ == "__main__":
    success = test_connection()
    print("-" * 50)
    if success:
        print("✅ Database setup is complete!")
    else:
        print("⚠️  Database setup incomplete. System will use file-based storage.")
    sys.exit(0 if success else 1)
