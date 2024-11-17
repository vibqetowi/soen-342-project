import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Administrator:
    """Administrator class representing system administrators."""
    
    def __init__(self, user_id: str, email: str, name: str):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.db = DatabaseConnection()

    def create_offering(self, lesson_type: str, mode: str, capacity: int, duration: int) -> str:
        """Create a new offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    offering_id = str(uuid.uuid4())
                    
                    # Insert offering
                    cur.execute("""
                        INSERT INTO offerings (offering_id, lesson_type, mode, capacity, duration)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING offering_id
                    """, (offering_id, lesson_type, mode, capacity, duration))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'offerings', %s, 'INSERT', 'offerings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        offering_id,
                        json.dumps({
                            'offering_id': offering_id,
                            'lesson_type': lesson_type,
                            'mode': mode,
                            'capacity': capacity,
                            'duration': duration
                        })
                    ))
                    
                    conn.commit()
                    return offering_id
                    
        except Exception as e:
            logger.error(f"Error creating offering: {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from the system."""
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
                                    log_id, timestamp, table_name, actor_id, action_type, 
                                    target_table, record_id, old_value
                                ) VALUES (%s, %s, %s, %s, 'DELETE', %s, %s, %s::jsonb)
                            """, (
                                str(uuid.uuid4()),
                                datetime.now(),
                                table,
                                self.user_id,
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

    def edit_user(self, user_id: str, table: str, updates: Dict[str, Any]) -> bool:
        """Edit user information."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute(f"""
                        SELECT *
                        FROM {table}
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False

                    # Build UPDATE query dynamically
                    set_clause = ', '.join(f"{key} = %s" for key in updates.keys())
                    query = f"""
                        UPDATE {table}
                        SET {set_clause}
                        WHERE user_id = %s
                    """
                    
                    # Execute update
                    cur.execute(query, list(updates.values()) + [user_id])
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, %s, %s, 'UPDATE', %s, %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        table,
                        self.user_id,
                        table,
                        user_id,
                        json.dumps(dict(zip([col.name for col in cur.description], old_data))),
                        json.dumps(updates)
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    def delete_booking(self, booking_id: Dict[str, str]) -> bool:
        """Delete a booking."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute("""
                        SELECT *
                        FROM bookings
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booking_id['booked_by_client_id'], booking_id['public_offering_id']))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False

                    # Delete booking
                    cur.execute("""
                        DELETE FROM bookings
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booking_id['booked_by_client_id'], booking_id['public_offering_id']))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, old_value
                        ) VALUES (%s, %s, 'bookings', %s, 'DELETE', 'bookings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        booking_id['public_offering_id'],
                        json.dumps(dict(zip([col.name for col in cur.description], old_data)))
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error deleting booking: {e}")
            raise

    def delete_offering(self, offering_id: str) -> bool:
        """Delete an offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute("""
                        SELECT *
                        FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False

                    # Delete offering
                    cur.execute("""
                        DELETE FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, old_value
                        ) VALUES (%s, %s, 'offerings', %s, 'DELETE', 'offerings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        offering_id,
                        json.dumps(dict(zip([col.name for col in cur.description], old_data)))
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error deleting offering: {e}")
            raise

    def edit_offering(self, offering_id: str, updates: Dict[str, Any]) -> bool:
        """Edit offering information."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute("""
                        SELECT *
                        FROM offerings
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    old_data = cur.fetchone()
                    if not old_data:
                        return False

                    # Build UPDATE query dynamically
                    set_clause = ', '.join(f"{key} = %s" for key in updates.keys())
                    query = f"""
                        UPDATE offerings
                        SET {set_clause}
                        WHERE offering_id = %s
                    """
                    
                    # Execute update
                    cur.execute(query, list(updates.values()) + [offering_id])
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'offerings', %s, 'UPDATE', 'offerings', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        offering_id,
                        json.dumps(dict(zip([col.name for col in cur.description], old_data))),
                        json.dumps(updates)
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating offering: {e}")
            raise

    def __repr__(self):
        return f"Administrator(user_id={self.user_id}, email='{self.email}', name='{self.name}')"

if __name__ == "__main__":
    # Example usage
    try:
        # Create an administrator instance
        admin = Administrator(
            user_id=str(uuid.uuid4()),
            email="admin@example.com",
            name="Admin User"
        )
        
        # Create a new offering
        offering_id = admin.create_offering(
            lesson_type="Piano",
            mode="group",
            capacity=10,
            duration=60
        )
        logger.info(f"Created offering with ID: {offering_id}")
        
        # Edit the offering
        success = admin.edit_offering(
            offering_id=offering_id,
            updates={'capacity': 15, 'duration': 90}
        )
        logger.info(f"Updated offering: {success}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")