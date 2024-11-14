import psycopg2
import json
from pathlib import Path
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_secrets():
    """Load database connection parameters from .secrets file"""
    try:
        secrets_path = Path(__file__).parent / '.secrets'
        if not secrets_path.exists():
            raise FileNotFoundError("'.secrets' file not found!")
        
        with open(secrets_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading .secrets file: {e}")
        raise

def get_admin_connection():
    """Create a connection to postgres database for admin operations"""
    secrets = load_secrets()
    
    # Create a copy of secrets and modify for admin connection
    admin_params = secrets.copy()
    admin_params['database'] = 'postgres'  # Connect to default postgres database
    
    try:
        conn = psycopg2.connect(**admin_params)
        conn.autocommit = True  # Required for database creation/deletion
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def get_db_connection(dbname):
    """Create a connection to the specified database"""
    secrets = load_secrets()
    secrets['database'] = dbname
    
    try:
        return psycopg2.connect(**secrets)
    except Exception as e:
        logger.error(f"Error connecting to database {dbname}: {e}")
        raise

def setup_database():
    """Setup the database by dropping if exists and recreating"""
    secrets = load_secrets()
    dbname = secrets.get('dbname')
    
    # Connect to postgres database to perform admin operations
    with get_admin_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # First, disconnect all other clients
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{dbname}'
                    AND pid <> pg_backend_pid()
                """)
                
                # Drop database if exists
                logger.info(f"Dropping database {dbname} if exists...")
                cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
                
                # Create new database
                logger.info(f"Creating database {dbname}...")
                cursor.execute(f"CREATE DATABASE {dbname}")
                
                logger.info(f"Database {dbname} created successfully")
                
            except Exception as e:
                logger.error(f"Error setting up database: {e}")
                raise

def execute_ddl():
    """Execute the DDL commands from ddl.sql file"""
    secrets = load_secrets()
    dbname = secrets.get('dbname')
    
    # Load DDL file
    ddl_path = Path(__file__).parent / 'DDL-342-project.sql'
    if not ddl_path.exists():
        raise FileNotFoundError("ddl.sql file not found!")
    
    with open(ddl_path, 'r') as f:
        ddl_commands = f.read()
    
    # Connect to the new database and execute DDL
    with get_db_connection(dbname) as conn:
        with conn.cursor() as cursor:
            try:
                logger.info("Executing DDL commands...")
                cursor.execute(ddl_commands)
                conn.commit()
                logger.info("DDL execution completed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Error executing DDL: {e}")
                raise

def main():
    try:
        # Setup database
        setup_database()
        
        # Execute DDL
        execute_ddl()
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()