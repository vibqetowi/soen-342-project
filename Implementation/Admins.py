import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime
import logging
import bcrypt
from singleton_decorator import singleton
from typing import List, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@singleton
class AdministratorCatalog:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_administrator(self, email: str, password: str, name: str) -> 'Administrator':
        """Create a new administrator."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    user_id = str(uuid.uuid4())
                    
                    # Hash the password
                    hashed_password = bcrypt.hashpw(
                        password.encode('utf-8'), 
                        bcrypt.gensalt()
                    ).decode('utf-8')
                    
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
                    
        except psycopg2.IntegrityError as e:
            if 'email' in str(e):
                logger.error("Email already exists")
                raise ValueError("Email already exists")
            raise
        except Exception as e:
            logger.error(f"Error creating administrator: {e}")
            raise

    def get_administrator(self, user_id: str) -> Optional['Administrator']:
        """Retrieve an administrator by their ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, email, name
                        FROM administrators 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return Administrator(
                            result['user_id'],
                            result['email'],
                            result['name']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving administrator: {e}")
            raise

    def get_administrator_by_email(self, email: str) -> Optional['Administrator']:
        """Retrieve an administrator by their email."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, email, name
                        FROM administrators 
                        WHERE email = %s
                    """, (email,))
                    
                    result = cur.fetchone()
                    if result:
                        return Administrator(
                            result['user_id'],
                            result['email'],
                            result['name']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving administrator by email: {e}")
            raise

    def update_administrator(self, user_id: str, **kwargs) -> bool:
        """Update administrator information."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current state for audit log
                    cur.execute("""
                        SELECT email, name
                        FROM administrators
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False
                    
                    # Build update query dynamically
                    valid_fields = {'email', 'name', 'hashed_password'}
                    update_fields = []
                    update_values = []
                    
                    for key, value in kwargs.items():
                        if key in valid_fields:
                            update_fields.append(f"{key} = %s")
                            update_values.append(value)
                    
                    if not update_fields:
                        return False
                    
                    # Add user_id for WHERE clause
                    update_values.append(user_id)
                    
                    # Execute update
                    query = f"""
                        UPDATE administrators 
                        SET {", ".join(update_fields)}
                        WHERE user_id = %s
                    """
                    cur.execute(query, update_values)
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'administrators', 'UPDATE', 'administrators', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        user_id,
                        json.dumps(dict(zip(['email', 'name'], old_data))),
                        json.dumps(kwargs)
                    ))
                    
                    conn.commit()
                    return True
                    
        except psycopg2.IntegrityError as e:
            if 'email' in str(e):
                logger.error("Email already exists")
                raise ValueError("Email already exists")
            raise
        except Exception as e:
            logger.error(f"Error updating administrator: {e}")
            raise

    def delete_administrator(self, user_id: str) -> bool:
        """Delete an administrator."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current state for audit log
                    cur.execute("""
                        SELECT email, name
                        FROM administrators
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False
                    
                    # Delete administrator
                    cur.execute("""
                        DELETE FROM administrators
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value
                        ) VALUES (%s, %s, 'administrators', 'DELETE', 'administrators', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        user_id,
                        json.dumps(dict(zip(['email', 'name'], old_data)))
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error deleting administrator: {e}")
            raise

    def authenticate_administrator(self, email: str, password: str) -> Optional['Administrator']:
        """Authenticate an administrator using email and password."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT user_id, email, name, hashed_password
                        FROM administrators 
                        WHERE email = %s
                    """, (email,))
                    
                    result = cur.fetchone()
                    if result and bcrypt.checkpw(
                        password.encode('utf-8'),
                        result['hashed_password'].encode('utf-8')
                    ):
                        return Administrator(
                            result['user_id'],
                            result['email'],
                            result['name']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating administrator: {e}")
            raise

class Administrator:
    def __init__(self, user_id: str, email: str, name: str):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.db = DatabaseConnection()

    def __repr__(self):
        return f"Administrator(user_id={self.user_id}, email='{self.email}', name='{self.name}')"

    def update_offering(self, offering_id: str, **kwargs) -> bool:
        """Update an offering's information."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current state for audit log
                    cur.execute("""
                        SELECT lesson_type, mode, capacity, duration
                        FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False
                    
                    # Build update query dynamically
                    valid_fields = {'lesson_type', 'mode', 'capacity', 'duration'}
                    update_fields = []
                    update_values = []
                    
                    for key, value in kwargs.items():
                        if key in valid_fields:
                            update_fields.append(f"{key} = %s")
                            update_values.append(value)
                    
                    if not update_fields:
                        return False
                    
                    # Add offering_id for WHERE clause
                    update_values.append(offering_id)
                    
                    # Execute update
                    query = f"""
                        UPDATE offerings 
                        SET {", ".join(update_fields)}
                        WHERE offering_id = %s
                    """
                    cur.execute(query, update_values)
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value,
                            actor_id
                        ) VALUES (%s, %s, 'offerings', 'UPDATE', 'offerings', %s, %s::jsonb, %s::jsonb, %s)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        offering_id,
                        json.dumps(dict(zip(
                            ['lesson_type', 'mode', 'capacity', 'duration'],
                            old_data
                        ))),
                        json.dumps(kwargs),
                        self.user_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating offering: {e}")
            raise

    def delete_offering(self, offering_id: str) -> bool:
        """Delete an offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current state for audit log
                    cur.execute("""
                        SELECT lesson_type, mode, capacity, duration
                        FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False
                    
                    # Delete offering (cascades will handle related records)
                    cur.execute("""
                        DELETE FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, actor_id
                        ) VALUES (%s, %s, 'offerings', 'DELETE', 'offerings', %s, %s::jsonb, %s)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        offering_id,
                        json.dumps(dict(zip(
                            ['lesson_type', 'mode', 'capacity', 'duration'],
                            old_data
                        ))),
                        self.user_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error deleting offering: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    try:
        admin_catalog = AdministratorCatalog()
        
        # Create an administrator
        admin = admin_catalog.create_administrator(
            email="admin@example.com",
            password="secure_password",
            name="John Admin"
        )
        logger.info(f"Created administrator: {admin}")
        
        # Authenticate
        authenticated_admin = admin_catalog.authenticate_administrator(
            "admin@example.com",
            "secure_password"
        )
        logger.info(f"Authenticated administrator: {authenticated_admin}")
        
        # Update an offering
        if authenticated_admin:
            success = authenticated_admin.update_offering(
                str(uuid.uuid4()),  # In real usage, this would be a valid offering ID
                capacity=20,
                duration=60
            )
            logger.info(f"Updated offering: {success}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")