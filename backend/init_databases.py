"""
Database initialization script.
Creates SQLite databases from SQL schema files.
"""
import os
import sqlite3
import sys

def init_database(db_path: str, schema_path: str):
    """Initialize database from SQL schema file."""
    print(f"Initializing {db_path}...")
    
    # Read schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"✓ Successfully initialized {db_path}")
        
        # Count records
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  Tables created: {[t[0] for t in tables]}")
        
        for table in tables:
            if table[0] != 'sqlite_sequence':
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  {table[0]}: {count} records")
        
        return True
    except Exception as e:
        print(f"✗ Error initializing {db_path}: {e}")
        return False
    finally:
        conn.close()

def main():
    """Initialize all databases."""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chat_data_dir = os.path.join(script_dir, 'Chat', 'data')
    
    # Ensure data directory exists
    os.makedirs(chat_data_dir, exist_ok=True)
    
    # Initialize databases
    databases = [
        (
            os.path.join(chat_data_dir, 'drugs.db'),
            os.path.join(chat_data_dir, 'drugs.sql')
        ),
        (
            os.path.join(chat_data_dir, 'history.db'),
            os.path.join(chat_data_dir, 'history.sql')
        )
    ]
    
    success_count = 0
    for db_path, schema_path in databases:
        if not os.path.exists(schema_path):
            print(f"✗ Schema file not found: {schema_path}")
            continue
        
        if init_database(db_path, schema_path):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"Initialization complete: {success_count}/{len(databases)} successful")
    print("=" * 60)
    
    if success_count == len(databases):
        print("\n✓ All databases initialized successfully!")
        print("\nNext steps:")
        print("1. Add your GROQ_API_KEY to ../.env")
        print("2. Install Chat dependencies: cd Chat && pip install -r requirements.txt")
        print("3. Run Chat service: python Chat/run.py")
        print("4. Install Relapse dependencies: cd Relapse && pip install -r requirements.txt")
        print("5. Run Relapse service: python Relapse/run.py")
    else:
        print("\n⚠ Some databases failed to initialize. Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
