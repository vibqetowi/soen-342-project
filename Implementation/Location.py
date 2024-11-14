import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from pathlib import Path
import logging
from datetime import datetime
from singleton_decorator import singleton

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@singleton
class DatabaseConnection:
    def __init__(self):
        self.conn_params = self._load_connection_params()
    
    def _load_connection_params(self):
        secrets_path = Path(__file__).parent / '.secrets'
        with open(secrets_path, 'r') as f:
            return json.load(f)
    
    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

@singleton
class LocationCatalog:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_province(self, name: str) -> 'Province':
        """Create a new province in the database."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    location_id = str(uuid.uuid4())
                    
                    # Insert province
                    cur.execute("""
                        INSERT INTO provinces (location_id, name)
                        VALUES (%s, %s)
                        RETURNING location_id
                    """, (location_id, name))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'provinces', 'INSERT', 'provinces', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        location_id,
                        json.dumps({'location_id': location_id, 'name': name})
                    ))
                    
                    conn.commit()
                    return Province(location_id, name)
                    
        except Exception as e:
            logger.error(f"Error creating province: {e}")
            raise

    def get_province(self, location_id: str) -> 'Province':
        """Retrieve a province by its ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT location_id, name 
                        FROM provinces 
                        WHERE location_id = %s
                    """, (location_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return Province(result['location_id'], result['name'])
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving province: {e}")
            raise

    def get_province_by_name(self, name: str) -> 'Province':
        """Retrieve a province by its name."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT location_id, name 
                        FROM provinces 
                        WHERE name = %s
                    """, (name,))
                    
                    result = cur.fetchone()
                    if result:
                        return Province(result['location_id'], result['name'])
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving province by name: {e}")
            raise

    def get_city(self, city_id: str) -> 'City':
        """Retrieve a city by its ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT location_id, name, parent_location_id
                        FROM cities 
                        WHERE location_id = %s
                    """, (city_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return City(result['location_id'], result['name'], result['parent_location_id'])
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving city: {e}")
            raise

    def get_branch(self, branch_id: str) -> 'Branch':
        """Retrieve a branch by its ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT location_id, name, parent_location_id, schedule_id
                        FROM branches 
                        WHERE location_id = %s
                    """, (branch_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return Branch(
                            result['location_id'], 
                            result['name'], 
                            result['parent_location_id'],
                            result['schedule_id']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving branch: {e}")
            raise

class Province:
    def __init__(self, location_id: str, name: str):
        self.location_id = location_id
        self.name = name
        self.db = DatabaseConnection()

    def create_city(self, name: str) -> 'City':
        """Create a new city in this province."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    location_id = str(uuid.uuid4())
                    
                    # Insert city
                    cur.execute("""
                        INSERT INTO cities (location_id, name, parent_location_id)
                        VALUES (%s, %s, %s)
                        RETURNING location_id
                    """, (location_id, name, self.location_id))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'cities', 'INSERT', 'cities', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        location_id,
                        json.dumps({
                            'location_id': location_id,
                            'name': name,
                            'parent_location_id': self.location_id
                        })
                    ))
                    
                    conn.commit()
                    return City(location_id, name, self.location_id)
                    
        except Exception as e:
            logger.error(f"Error creating city: {e}")
            raise

class City:
    def __init__(self, location_id: str, name: str, parent_location_id: str):
        self.location_id = location_id
        self.name = name
        self.parent_location_id = parent_location_id
        self.db = DatabaseConnection()

    def create_branch(self, name: str, schedule_id: str) -> 'Branch':
        """Create a new branch in this city."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    location_id = str(uuid.uuid4())
                    
                    # Insert branch
                    cur.execute("""
                        INSERT INTO branches (location_id, name, schedule_id, parent_location_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING location_id
                    """, (location_id, name, schedule_id, self.location_id))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'branches', 'INSERT', 'branches', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        location_id,
                        json.dumps({
                            'location_id': location_id,
                            'name': name,
                            'schedule_id': schedule_id,
                            'parent_location_id': self.location_id
                        })
                    ))
                    
                    conn.commit()
                    return Branch(location_id, name, self.location_id, schedule_id)
                    
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise

class Branch:
    def __init__(self, location_id: str, name: str, parent_location_id: str, schedule_id: str):
        self.location_id = location_id
        self.name = name
        self.parent_location_id = parent_location_id
        self.schedule_id = schedule_id
        self.db = DatabaseConnection()

if __name__ == "__main__":
    # Example usage
    try:
        location_catalog = LocationCatalog()
        
        # Create a province
        province = location_catalog.create_province("California")
        logger.info(f"Created province: {province.name} with ID: {province.location_id}")
        
        # Create a city in the province
        city = province.create_city("Los Angeles")
        logger.info(f"Created city: {city.name} with ID: {city.location_id}")
        
        # Create a branch in the city (assuming we have a schedule_id)
        schedule_id = str(uuid.uuid4())  # In real usage, this would come from ScheduleCatalog
        branch = city.create_branch("Downtown LA Branch", schedule_id)
        logger.info(f"Created branch: {branch.name} with ID: {branch.location_id}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")