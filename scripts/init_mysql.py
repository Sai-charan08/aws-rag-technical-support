import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from src.database.mysql_db import get_db_manager
from src.auth.auth_service import get_auth_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("=== Initializing Database (MySQL / Fallback) ===")
    db = get_db_manager()
    stats = db.get_stats()
    
    print("\n" + "=" * 60)
    print("           DATABASE INITIALIZATION & STATUS REPORT")
    print("=" * 60)
    print(f"Database Engine   : {stats['engine']}")
    print(f"Target Database   : {stats['database']}")
    print(f"Target Host       : {stats['host']}")
    print(f"MySQL Connected?  : {'YES' if stats['is_mysql'] else 'NO (Using SQLite Fallback)'}")
    print(f"Total Users       : {stats['total_users']}")
    print(f"Total Logged Chats: {stats['total_queries']}")
    print("=" * 60 + "\n")

    auth = get_auth_service()
    print("[SUCCESS] Users and tables verified. Demo users initialized.")

if __name__ == "__main__":
    main()

