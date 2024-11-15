import uuid
import psycopg2
from psycopg2.extras import DictCursor
import json
from datetime import datetime, timedelta
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
class ScheduleCatalog:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_schedule(self, table_name: str, record_id: str) -> 'Schedule':
        """Creates a new schedule and adds it to the catalog."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    schedule_id = str(uuid.uuid4())
                    
                    # Insert schedule
                    cur.execute("""
                        INSERT INTO schedules (schedule_id, table_name, record_id)
                        VALUES (%s, %s, %s)
                        RETURNING schedule_id
                    """, (schedule_id, table_name, record_id))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, new_value
                        ) VALUES (%s, %s, 'schedules', 'INSERT', 'schedules', %s, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        schedule_id,
                        json.dumps({
                            'schedule_id': schedule_id,
                            'table_name': table_name,
                            'record_id': record_id
                        })
                    ))
                    
                    conn.commit()
                    schedule = Schedule(schedule_id, table_name, record_id)
                    schedule.generate_time_slots()  # Generate initial time slots
                    return schedule
                    
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise

    def get_schedule(self, schedule_id: str) -> Optional['Schedule']:
        """Retrieves a schedule by its ID."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT schedule_id, table_name, record_id
                        FROM schedules 
                        WHERE schedule_id = %s
                    """, (schedule_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return Schedule(
                            result['schedule_id'],
                            result['table_name'],
                            result['record_id']
                        )
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving schedule: {e}")
            raise

    def get_schedules_by_record(self, table_name: str, record_id: str) -> List['Schedule']:
        """Retrieves all schedules for a specific record."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT schedule_id, table_name, record_id
                        FROM schedules 
                        WHERE table_name = %s AND record_id = %s
                    """, (table_name, record_id))
                    
                    return [
                        Schedule(
                            row['schedule_id'],
                            row['table_name'],
                            row['record_id']
                        )
                        for row in cur.fetchall()
                    ]
                    
        except Exception as e:
            logger.error(f"Error retrieving schedules by record: {e}")
            raise

class Schedule:
    def __init__(self, schedule_id: str, table_name: str, record_id: str):
        self.schedule_id = schedule_id
        self.table_name = table_name
        self.record_id = record_id
        self.db = DatabaseConnection()

    def generate_time_slots(self):
        """Generates time slots for the next week in 30-minute increments."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    today = datetime.now()
                    end_date = today + timedelta(days=7)
                    current_time = today.replace(hour=0, minute=0, second=0, microsecond=0)

                    # Delete old time slots first
                    self.delete_old_time_slots()

                    # Generate new time slots
                    while current_time < end_date:
                        end_time = current_time + timedelta(minutes=30)
                        
                        cur.execute("""
                            INSERT INTO time_slots (
                                schedule_id, start_time, end_time, is_reserved
                            ) VALUES (%s, %s, %s, %s)
                            ON CONFLICT (schedule_id, start_time) DO NOTHING
                        """, (
                            self.schedule_id,
                            current_time,
                            end_time,
                            False
                        ))
                        
                        current_time += timedelta(minutes=30)
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Error generating time slots: {e}")
            raise

    def delete_old_time_slots(self):
        """Deletes time slots older than today."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Get old time slots for audit log
                    cur.execute("""
                        SELECT start_time, end_time, is_reserved
                        FROM time_slots
                        WHERE schedule_id = %s AND start_time < %s
                    """, (self.schedule_id, today))
                    
                    old_slots = cur.fetchall()
                    
                    # Delete old time slots
                    cur.execute("""
                        DELETE FROM time_slots
                        WHERE schedule_id = %s AND start_time < %s
                    """, (self.schedule_id, today))
                    
                    # Create audit log if slots were deleted
                    if old_slots:
                        cur.execute("""
                            INSERT INTO audit_logs (
                                log_id, timestamp, table_name, action_type, 
                                target_table, record_id, old_value
                            ) VALUES (%s, %s, 'time_slots', 'DELETE', 'time_slots', %s, %s::jsonb)
                        """, (
                            str(uuid.uuid4()),
                            datetime.now(),
                            self.schedule_id,
                            json.dumps([{
                                'start_time': str(slot[0]),
                                'end_time': str(slot[1]),
                                'is_reserved': slot[2]
                            } for slot in old_slots])
                        ))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Error deleting old time slots: {e}")
            raise

    def get_available_slots(self) -> List[Dict]:
        """Returns a list of available time slots."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT start_time, end_time
                        FROM time_slots
                        WHERE schedule_id = %s 
                        AND is_reserved = FALSE
                        ORDER BY start_time
                    """, (self.schedule_id,))
                    
                    return cur.fetchall()
                    
        except Exception as e:
            logger.error(f"Error retrieving available slots: {e}")
            raise

    def get_reserved_slots(self) -> List[Dict]:
        """Returns a list of reserved time slots."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT start_time, end_time, reserved_by_public_offering_id
                        FROM time_slots
                        WHERE schedule_id = %s 
                        AND is_reserved = TRUE
                        ORDER BY start_time
                    """, (self.schedule_id,))
                    
                    return cur.fetchall()
                    
        except Exception as e:
            logger.error(f"Error retrieving reserved slots: {e}")
            raise

    def reserve_slot(self, start_time: datetime, public_offering_id: str) -> bool:
        """Reserves a specific time slot."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if slot is available
                    cur.execute("""
                        SELECT is_reserved
                        FROM time_slots
                        WHERE schedule_id = %s AND start_time = %s
                    """, (self.schedule_id, start_time))
                    
                    result = cur.fetchone()
                    if not result or result[0]:
                        return False
                    
                    # Reserve the slot
                    cur.execute("""
                        UPDATE time_slots
                        SET is_reserved = TRUE, reserved_by_public_offering_id = %s
                        WHERE schedule_id = %s AND start_time = %s
                    """, (public_offering_id, self.schedule_id, start_time))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'time_slots', 'UPDATE', 'time_slots', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.schedule_id,
                        json.dumps({'is_reserved': False}),
                        json.dumps({
                            'is_reserved': True,
                            'reserved_by_public_offering_id': public_offering_id
                        })
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error reserving slot: {e}")
            raise

    def cancel_reservation(self, start_time: datetime) -> bool:
        """Cancels a reservation for a specific time slot."""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current state for audit log
                    cur.execute("""
                        SELECT is_reserved, reserved_by_public_offering_id
                        FROM time_slots
                        WHERE schedule_id = %s AND start_time = %s
                    """, (self.schedule_id, start_time))
                    
                    result = cur.fetchone()
                    if not result or not result[0]:
                        return False
                    
                    old_offering_id = result[1]
                    
                    # Cancel the reservation
                    cur.execute("""
                        UPDATE time_slots
                        SET is_reserved = FALSE, reserved_by_public_offering_id = NULL
                        WHERE schedule_id = %s AND start_time = %s
                    """, (self.schedule_id, start_time))
                    
                    # Create audit log
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, action_type, 
                            target_table, record_id, old_value, new_value
                        ) VALUES (%s, %s, 'time_slots', 'UPDATE', 'time_slots', %s, %s::jsonb, %s::jsonb)
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        self.schedule_id,
                        json.dumps({
                            'is_reserved': True,
                            'reserved_by_public_offering_id': old_offering_id
                        }),
                        json.dumps({'is_reserved': False, 'reserved_by_public_offering_id': None})
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Error canceling reservation: {e}")
            raise

    def __repr__(self):
        return f"Schedule(id={self.schedule_id}, table={self.table_name}, record={self.record_id})"

if __name__ == "__main__":
    # Example usage
    try:
        catalog = ScheduleCatalog()
        
        # Create a schedule for an instructor
        instructor_id = str(uuid.uuid4())  # In real usage, this would be a valid instructor ID
        schedule = catalog.create_schedule("instructors", instructor_id)
        logger.info(f"Created schedule: {schedule}")
        
        # Get available slots
        available_slots = schedule.get_available_slots()
        logger.info(f"Available slots: {len(available_slots)}")
        
        # Reserve a slot
        if available_slots:
            first_slot = available_slots[0]
            public_offering_id = str(uuid.uuid4())  # In real usage, this would be a valid offering ID
            success = schedule.reserve_slot(first_slot['start_time'], public_offering_id)
            logger.info(f"Reserved slot: {success}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")