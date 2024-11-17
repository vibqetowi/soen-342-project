import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime
import logging
from typing import List, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Instructor:
    def __init__(self, user_id: str, email: str, name: str, phone: str, 
                 specialization: str, schedule_id: str):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.phone = phone
        self.specialization = specialization
        self.schedule_id = schedule_id
        self.db = DatabaseConnection()

    def update_profile(self, **kwargs) -> bool:
        """Update instructor profile information."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute("""
                        SELECT * FROM instructors WHERE user_id = %s
                    """, (self.user_id,))
                    old_data = dict(zip([col.name for col in cur.description], cur.fetchone()))

                    # Build update query dynamically based on provided fields
                    valid_fields = {'name', 'phone', 'specialization', 'schedule_id'}
                    update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
                    
                    if not update_fields:
                        return False

                    query_parts = [f"{k} = %s" for k in update_fields.keys()]
                    query = f"""
                        UPDATE instructors 
                        SET {', '.join(query_parts)}
                        WHERE user_id = %s
                    """
                    
                    # Execute update
                    cur.execute(
                        query,
                        list(update_fields.values()) + [self.user_id]
                    )
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'instructors', 'UPDATE', 'instructors', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        json.dumps(old_data),
                        json.dumps(update_fields)
                    ))
                    
                    conn.commit()
                    
                    # Update instance attributes
                    for k, v in update_fields.items():
                        setattr(self, k, v)
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Error updating instructor profile: {e}")
            raise

    def set_branch_availability(self, branch_id: str) -> bool:
        """Add a branch to the instructor's availability."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO instructor_branch_availability (instructor_id, branch_id)
                        VALUES (%s, %s)
                        ON CONFLICT (instructor_id, branch_id) DO NOTHING
                        RETURNING instructor_id
                    """, (self.user_id, branch_id))
                    
                    if cur.fetchone():
                        # Create audit log
                        cur.execute("""
                            INSERT INTO audit_logs (
                                log_id, timestamp, table_name, action_type, 
                                target_table, record_id, new_value
                            ) VALUES (%s, %s, 'instructor_branch_availability', 'INSERT', 
                                     'instructor_branch_availability', %s, %s::jsonb)
                        """, (
                            str(uuid.uuid4()),
                            datetime.now(),
                            self.user_id,
                            json.dumps({
                                'instructor_id': self.user_id,
                                'branch_id': branch_id
                            })
                        ))
                        
                        conn.commit()
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting branch availability: {e}")
            raise

    def remove_branch_availability(self, branch_id: str) -> bool:
        """Remove a branch from the instructor's availability."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current data for audit log
                    cur.execute("""
                        SELECT * FROM instructor_branch_availability
                        WHERE instructor_id = %s AND branch_id = %s
                    """, (self.user_id, branch_id))
                    old_data = cur.fetchone()
                    
                    if not old_data:
                        return False

                    # Remove availability
                    cur.execute("""
                        DELETE FROM instructor_branch_availability
                        WHERE instructor_id = %s AND branch_id = %s
                    """, (self.user_id, branch_id))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value
                        ) VALUES (%s, %s, 'instructor_branch_availability', 'DELETE', 
                                 'instructor_branch_availability', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.user_id,
                        json.dumps({
                            'instructor_id': self.user_id,
                            'branch_id': branch_id
                        })
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error removing branch availability: {e}")
            raise

    def get_available_branches(self) -> List[Dict]:
        """Get all branches where the instructor is available."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT b.* 
                        FROM branches b
                        JOIN instructor_branch_availability iba 
                        ON b.location_id = iba.branch_id
                        WHERE iba.instructor_id = %s
                    """, (self.user_id,))
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting available branches: {e}")
            raise

    def get_public_offerings(self) -> List[Dict]:
        """Get all public offerings associated with this instructor."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT po.*, o.lesson_type, o.mode, o.capacity, o.duration
                        FROM public_offerings po
                        JOIN offerings o ON po.offering_id = o.offering_id
                        WHERE po.instructor_id = %s
                    """, (self.user_id,))
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting public offerings: {e}")
            raise

    def get_bookings(self) -> List[Dict]:
        """Get all bookings for this instructor's offerings."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT b.*, c.name as client_name
                        FROM bookings b
                        JOIN clients c ON b.booked_by_client_id = c.user_id
                        JOIN public_offerings po ON b.public_offering_id = po.offering_id
                        WHERE po.instructor_id = %s
                    """, (self.user_id,))
                    
                    return [dict(row) for row in cur.fetchall()]
                    
        except Exception as e:
            logger.error(f"Error getting bookings: {e}")
            raise

    def create_offering(self, lesson_type: str, mode: str, capacity: int, duration: int) -> Dict:
        """Create a new offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    offering_id = str(uuid.uuid4())
                    
                    # Create base offering
                    cur.execute("""
                        INSERT INTO offerings (offering_id, lesson_type, mode, capacity, duration)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                    """, (offering_id, lesson_type, mode, capacity, duration))
                    
                    offering = dict(cur.fetchone())
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'offerings', 'INSERT', 'offerings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        offering_id,
                        json.dumps(offering)
                    ))
                    
                    conn.commit()
                    return offering
                    
        except Exception as e:
            logger.error(f"Error creating offering: {e}")
            raise

    def create_public_offering(self, offering_id: str, schedule_id: str,
                             lesson_type: str, mode: str, capacity: int) -> Dict:
        """Create a public offering from an existing offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Create public offering
                    cur.execute("""
                        INSERT INTO public_offerings (
                            offering_id, instructor_id, schedule_id, 
                            lesson_type, mode, capacity
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """, (
                        offering_id, self.user_id, schedule_id,
                        lesson_type, mode, capacity
                    ))
                    
                    public_offering = dict(cur.fetchone())
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'public_offerings', 'INSERT', 'public_offerings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        offering_id,
                        json.dumps(public_offering)
                    ))
                    
                    conn.commit()
                    return public_offering
                    
        except Exception as e:
            logger.error(f"Error creating public offering: {e}")
            raise

    def __repr__(self):
        return (f"Instructor(user_id={self.user_id}, name='{self.name}', "
                f"specialization='{self.specialization}', email='{self.email}')")

if __name__ == "__main__":
    # Example usage
    try:
        # Create an instructor
        instructor = Instructor(
            user_id=str(uuid.uuid4()),
            email="instructor@example.com",
            name="John Smith",
            phone="123-456-7890",
            specialization="Piano",
            schedule_id=str(uuid.uuid4())
        )
        
        # Create an offering
        offering = instructor.create_offering(
            lesson_type="Piano",
            mode="group",
            capacity=10,
            duration=60
        )
        logger.info(f"Created offering: {offering}")
        
        # Create a public offering
        public_offering = instructor.create_public_offering(
            offering_id=offering['offering_id'],
            schedule_id=str(uuid.uuid4()),
            lesson_type=offering['lesson_type'],
            mode=offering['mode'],
            capacity=offering['capacity']
        )
        logger.info(f"Created public offering: {public_offering}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")