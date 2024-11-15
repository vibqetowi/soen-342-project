import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime
import logging
from singleton_decorator import singleton
from typing import Optional, Union
import bcrypt

# Import user types from their respective modules
from Admins import Administrator
from Instructors import Instructor
from Clients import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@singleton
class UserCatalog:
    def __init__(self):
        self.db = DatabaseConnection()

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def register_client(self, email: str, password: str, name: str, schedule_id: str, 
                       age: int = None, guardian_id: str = None) -> Client:
        """Register a new client."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    user_id = str(uuid.uuid4())
                    hashed_password = self._hash_password(password)
                    
                    # Insert client
                    cur.execute("""
                        INSERT INTO clients (
                            user_id, email, hashed_password, name, 
                            schedule_id, age, guardian_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING user_id
                    """, (
                        user_id, email, hashed_password, name,
                        schedule_id, age, guardian_id
                    ))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'clients', 'INSERT', 'clients', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        user_id,
                        json.dumps({
                            'user_id': user_id,
                            'email': email,
                            'name': name,
                            'schedule_id': schedule_id,
                            'age': age,
                            'guardian_id': guardian_id
                        })
                    ))
                    
                    conn.commit()
                    return Client(user_id, email, name, schedule_id, age, guardian_id)
                    
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            raise

    def register_instructor(self, email: str, password: str, name: str, phone: str,
                          specialization: str, schedule_id: str) -> Instructor:
        """Register a new instructor."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    user_id = str(uuid.uuid4())
                    hashed_password = self._hash_password(password)
                    
                    # Insert instructor
                    cur.execute("""
                        INSERT INTO instructors (
                            user_id, email, hashed_password, name,
                            phone, specialization, schedule_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING user_id
                    """, (
                        user_id, email, hashed_password, name,
                        phone, specialization, schedule_id
                    ))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'instructors', 'INSERT', 'instructors', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        user_id,
                        json.dumps({
                            'user_id': user_id,
                            'email': email,
                            'name': name,
                            'phone': phone,
                            'specialization': specialization,
                            'schedule_id': schedule_id
                        })
                    ))
                    
                    conn.commit()
                    return Instructor(user_id, email, name, phone, specialization, schedule_id)
                    
        except Exception as e:
            logger.error(f"Error registering instructor: {e}")
            raise

    def register_administrator(self, email: str, password: str, name: str) -> Administrator:
        """Register a new administrator."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    user_id = str(uuid.uuid4())
                    hashed_password = self._hash_password(password)
                    
                    # Insert administrator
                    cur.execute("""
                        INSERT INTO administrators (
                            user_id, email, hashed_password, name
                        ) VALUES (%s, %s, %s, %s)
                        RETURNING user_id
                    """, (user_id, email, hashed_password, name))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'administrators', 'INSERT', 'administrators', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        user_id,
                        json.dumps({
                            'user_id': user_id,
                            'email': email,
                            'name': name
                        })
                    ))
                    
                    conn.commit()
                    return Administrator(user_id, email, name)
                    
        except Exception as e:
            logger.error(f"Error registering administrator: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[Union[Client, Instructor, Administrator]]:
        """Retrieve a user by their ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Try each user type table
                    for table, cls in [
                        ('clients', Client),
                        ('instructors', Instructor),
                        ('administrators', Administrator)
                    ]:
                        cur.execute(f"""
                            SELECT *
                            FROM {table}
                            WHERE user_id = %s
                        """, (user_id,))
                        
                        result = cur.fetchone()
                        if result:
                            return cls(**dict(result))
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving user: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Union[Client, Instructor, Administrator]]:
        """Retrieve a user by their email."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Try each user type table
                    for table, cls in [
                        ('clients', Client),
                        ('instructors', Instructor),
                        ('administrators', Administrator)
                    ]:
                        cur.execute(f"""
                            SELECT *
                            FROM {table}
                            WHERE email = %s
                        """, (email,))
                        
                        result = cur.fetchone()
                        if result:
                            return cls(**dict(result))
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving user by email: {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from any user type table."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Try to delete from each user type table
                    for table in ['clients', 'instructors', 'administrators']:
                        # Get current data for audit log
                        cur.execute(f"""
                            SELECT *
                            FROM {table}
                            WHERE user_id = %s
                        """, (user_id,))
                        
                        old_data = cur.fetchone()
                        if old_data:
                            # Create audit log
                            cur.execute("""
                                INSERT INTO audit_logs (
                                    log_id, timestamp, table_name, action_type, 
                                    target_table, record_id, old_value
                                ) VALUES (%s, %s, %s, 'DELETE', %s, %s, %s::jsonb)
                            """, (
                                str(uuid.uuid4()),
                                datetime.now(),
                                table,
                                table,
                                user_id,
                                json.dumps(dict(zip([col.name for col in cur.description], old_data)))
                            ))
                            
                            # Delete the user
                            cur.execute(f"""
                                DELETE FROM {table}
                                WHERE user_id = %s
                            """, (user_id,))
                            
                            conn.commit()
                            return True
                    
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise

    def login(self, email: str, password: str) -> Optional[Union[Client, Instructor, Administrator]]:
        """Authenticate a user based on email and password."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Try each user type table
                    for table, cls in [
                        ('clients', Client),
                        ('instructors', Instructor),
                        ('administrators', Administrator)
                    ]:
                        cur.execute(f"""
                            SELECT *
                            FROM {table}
                            WHERE email = %s
                        """, (email,))
                        
                        user = cur.fetchone()
                        if user and self._verify_password(password, user['hashed_password']):
                            return cls(**dict(user))
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    try:
        catalog = UserCatalog()
        
        # Register a client
        client = catalog.register_client(
            email="client@example.com",
            password="securepass",
            name="John Doe",
            schedule_id=str(uuid.uuid4()),
            age=25
        )
        logger.info(f"Created client: {client}")
        
        # Try to login
        logged_in_user = catalog.login("client@example.com", "securepass")
        logger.info(f"Logged in user: {logged_in_user}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")