import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime
import logging
from singleton_decorator import singleton
from typing import List, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@singleton
class OfferingCatalog:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_offering(self, lesson_type: str, mode: str, capacity: int, duration: int) -> 'Offering':
        """Create a new offering with the specified details."""
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
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'offerings', 'INSERT', 'offerings', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
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
                    return Offering(offering_id, lesson_type, mode, capacity, duration)
                    
        except Exception as e:
            logger.error(f"Error creating offering: {e}")
            raise

    def create_public_offering(
        self, 
        offering_id: str, 
        instructor_id: str,
        schedule_id: str,
        lesson_type: str,
        mode: str,
        capacity: int
    ) -> 'PublicOffering':
        """Create a new public offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Verify offering exists
                    cur.execute("""
                        SELECT EXISTS(SELECT 1 FROM offerings WHERE offering_id = %s)
                    """, (offering_id,))
                    
                    if not cur.fetchone()[0]:
                        raise ValueError("Offering not found")
                    
                    # Insert public offering
                    cur.execute("""
                        INSERT INTO public_offerings 
                        (offering_id, instructor_id, schedule_id, lesson_type, mode, capacity)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING offering_id
                    """, (offering_id, instructor_id, schedule_id, lesson_type, mode, capacity))
                    
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
                        json.dumps({
                            'offering_id': offering_id,
                            'instructor_id': instructor_id,
                            'schedule_id': schedule_id,
                            'lesson_type': lesson_type,
                            'mode': mode,
                            'capacity': capacity
                        })
                    ))
                    
                    conn.commit()
                    return PublicOffering(
                        offering_id, instructor_id, schedule_id, 
                        lesson_type, mode, capacity
                    )
                    
        except Exception as e:
            logger.error(f"Error creating public offering: {e}")
            raise

    def get_offering(self, offering_id: str) -> Optional['Offering']:
        """Retrieve an offering by its ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT offering_id, lesson_type, mode, capacity, duration
                        FROM offerings 
                        WHERE offering_id = %s
                    """, (offering_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return Offering(
                            result['offering_id'],
                            result['lesson_type'],
                            result['mode'],
                            result['capacity'],
                            result['duration']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving offering: {e}")
            raise

    def get_public_offering(self, offering_id: str, instructor_id: str) -> Optional['PublicOffering']:
        """Retrieve a public offering by its composite key."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT offering_id, instructor_id, schedule_id, 
                               lesson_type, mode, capacity
                        FROM public_offerings 
                        WHERE offering_id = %s AND instructor_id = %s
                    """, (offering_id, instructor_id))
                    
                    result = cur.fetchone()
                    if result:
                        return PublicOffering(
                            result['offering_id'],
                            result['instructor_id'],
                            result['schedule_id'],
                            result['lesson_type'],
                            result['mode'],
                            result['capacity']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving public offering: {e}")
            raise

    def get_public_offerings_by_instructor(self, instructor_id: str) -> List['PublicOffering']:
        """Get all public offerings for a specific instructor."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT offering_id, instructor_id, schedule_id, 
                               lesson_type, mode, capacity
                        FROM public_offerings 
                        WHERE instructor_id = %s
                    """, (instructor_id,))
                    
                    return [
                        PublicOffering(
                            row['offering_id'],
                            row['instructor_id'],
                            row['schedule_id'],
                            row['lesson_type'],
                            row['mode'],
                            row['capacity']
                        )
                        for row in cur.fetchall()
                    ]
                    
        except Exception as e:
            logger.error(f"Error retrieving instructor's public offerings: {e}")
            raise

class Offering:
    def __init__(self, offering_id: str, lesson_type: str, mode: str, capacity: int, duration: int):
        self.offering_id = offering_id
        self.lesson_type = lesson_type
        self.mode = mode
        self.capacity = capacity
        self.duration = duration
        self.db = DatabaseConnection()

    def __repr__(self):
        return (f"Offering(offering_id={self.offering_id}, "
                f"lesson_type='{self.lesson_type}', mode='{self.mode}', "
                f"capacity={self.capacity}, duration={self.duration})")

class PublicOffering:
    def __init__(self, offering_id: str, instructor_id: str, schedule_id: str,
                 lesson_type: str, mode: str, capacity: int):
        self.offering_id = offering_id
        self.instructor_id = instructor_id
        self.schedule_id = schedule_id
        self.lesson_type = lesson_type
        self.mode = mode
        self.capacity = capacity
        self.db = DatabaseConnection()

    def __repr__(self):
        return (f"PublicOffering(offering_id={self.offering_id}, "
                f"instructor_id={self.instructor_id}, schedule_id={self.schedule_id}, "
                f"lesson_type='{self.lesson_type}', mode='{self.mode}', "
                f"capacity={self.capacity})")

    def get_bookings(self) -> List[Dict]:
        """Get all bookings for this public offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT booked_by_client_id, booked_for_client_id
                        FROM bookings 
                        WHERE public_offering_id = %s
                    """, (self.offering_id,))
                    
                    return cur.fetchall()
                    
        except Exception as e:
            logger.error(f"Error retrieving bookings: {e}")
            raise

    def get_time_slots(self) -> List[Dict]:
        """Get all time slots for this public offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT schedule_id, start_time, end_time, is_reserved
                        FROM time_slots 
                        WHERE reserved_by_public_offering_id = %s
                    """, (self.offering_id,))
                    
                    return cur.fetchall()
                    
        except Exception as e:
            logger.error(f"Error retrieving time slots: {e}")
            raise

    def adjust_capacity(self, new_capacity: int):
        """Adjust the capacity of the public offering."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE public_offerings 
                        SET capacity = %s
                        WHERE offering_id = %s AND instructor_id = %s
                    """, (new_capacity, self.offering_id, self.instructor_id))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'public_offerings', 'UPDATE', 'public_offerings', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.offering_id,
                        json.dumps({'capacity': self.capacity}),
                        json.dumps({'capacity': new_capacity})
                    ))
                    
                    conn.commit()
                    self.capacity = new_capacity
                    
        except Exception as e:
            logger.error(f"Error adjusting capacity: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    try:
        catalog = OfferingCatalog()
        
        # Create a basic offering
        offering = catalog.create_offering(
            lesson_type="Piano",
            mode="group",
            capacity=10,
            duration=60
        )
        logger.info(f"Created offering: {offering}")
        
        # Create a public offering
        public_offering = catalog.create_public_offering(
            offering_id=offering.offering_id,
            instructor_id=str(uuid.uuid4()),  # In real usage, this would be a valid instructor ID
            schedule_id=str(uuid.uuid4()),    # In real usage, this would be a valid schedule ID
            lesson_type=offering.lesson_type,
            mode=offering.mode,
            capacity=offering.capacity
        )
        logger.info(f"Created public offering: {public_offering}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")