from sqlalchemy import create_engine, text
from pathlib import Path
import os

# Path to the database
# Check both potential locations
db_path = Path("backend/data/practice.db")
if not db_path.exists():
    db_path = Path("c:/Users/User/Practice_Room/backend/data/practice.db")

print(f"Checking database at: {db_path}")

try:
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(user)"))
        columns = [row[1] for row in result]
        print(f"Columns in 'user' table: {columns}")
        
        required = ["current_streak", "last_completed_at"]
        missing = [col for col in required if col not in columns]
        
        if missing:
            print(f"FAIL: Missing columns: {missing}")
        else:
            print("SUCCESS: All required columns are present.")

except Exception as e:
    print(f"Error checking database: {e}")
