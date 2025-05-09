import sqlite3
import os

def run_migration(migration_file):
    """Run a migration SQL file on the database."""
    print(f"Running migration: {migration_file}")
    
    # Connect to the database
    conn = sqlite3.connect('portfolio.db')
    
    try:
        # Read the migration SQL file
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute the migration
        conn.executescript(migration_sql)
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error running migration: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    # Create migrations directory if it doesn't exist
    if not os.path.exists('migrations'):
        os.makedirs('migrations')
    
    # Run the latest migration
    migration_file = 'migrations/add_anonymous_tracking.sql'
    if os.path.exists(migration_file):
        run_migration(migration_file)
    else:
        print(f"Migration file not found: {migration_file}") 