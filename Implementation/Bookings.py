import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    
    def __init__(self):
        self.conn_params = self._load_connection_params()
    
    def _load_connection_params(self) -> dict:
        """
        Load database connection parameters from .secrets file
        Returns a dictionary with connection parameters
        """
        try:
            secrets_path = Path(__file__).parent / '.secrets'
            
            if not secrets_path.exists():
                raise FileNotFoundError(
                    "'.secrets' file not found. Please create one with the following format:\n"
                    "{\n"
                    '    "dbname": "your_database",\n'
                    '    "user": "your_user",\n'
                    '    "password": "your_password",\n'
                    '    "host": "localhost",\n'
                    '    "port": "5432"\n'
                    "}"
                )
            
            # Read and parse the .secrets file
            with open(secrets_path, 'r') as f:
                conn_params = json.load(f)
            
            # Validate required parameters
            required_params = ['dbname', 'user', 'password', 'host', 'port']
            missing_params = [param for param in required_params if param not in conn_params]
            
            if missing_params:
                raise KeyError(f"Missing required parameters in .secrets file: {', '.join(missing_params)}")
            
            return conn_params
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing .secrets file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading database configuration: {str(e)}")
            raise
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of DatabaseConnection"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection(self):
        """Get a new database connection using the loaded parameters"""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

class Booking:
    def __init__(self, booked_by_client_id: str, public_offering_id: str, booked_for_client_id: str):
        self.booked_by_client_id = booked_by_client_id
        self.public_offering_id = public_offering_id
        self.booked_for_client_id = booked_for_client_id
    
    def __repr__(self):
        return (f"Booking(booked_by_client_id={self.booked_by_client_id}, "
                f"public_offering_id={self.public_offering_id}, "
                f"booked_for_client_id={self.booked_for_client_id})")

class BookingCatalog:
    _instance = None
    
    def __init__(self):
        if BookingCatalog._instance is not None:
            raise Exception("BookingCatalog is a singleton class")
        else:
            BookingCatalog._instance = self
            self.db = DatabaseConnection.get_instance()
    
    @staticmethod
    def get_instance():
        if BookingCatalog._instance is None:
            BookingCatalog()
        return BookingCatalog._instance
    
    def add_booking(self, booking: Booking) -> bool:
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # First verify if the clients and offering exist
                    cur.execute("""
                        SELECT EXISTS(SELECT 1 FROM clients WHERE user_id = %s) AND
                               EXISTS(SELECT 1 FROM clients WHERE user_id = %s) AND
                               EXISTS(SELECT 1 FROM public_offerings WHERE offering_id = %s)
                    """, (booking.booked_by_client_id, booking.booked_for_client_id, booking.public_offering_id))
                    
                    if not cur.fetchone()[0]:
                        raise ValueError("Invalid client IDs or offering ID")
                    
                    # Check if the booking already exists
                    cur.execute("""
                        SELECT COUNT(*) FROM bookings 
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booking.booked_by_client_id, booking.public_offering_id))
                    
                    if cur.fetchone()[0] > 0:
                        raise ValueError("Booking already exists")
                    
                    # Insert the new booking
                    cur.execute("""
                        INSERT INTO bookings (booked_by_client_id, public_offering_id, booked_for_client_id)
                        VALUES (%s, %s, %s)
                    """, (booking.booked_by_client_id, booking.public_offering_id, booking.booked_for_client_id))
                    
                    # Create audit log entry
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, new_value
                        )
                        VALUES (
                            %s, %s, 'bookings', %s, 'INSERT', 'bookings', %s,
                            %s::jsonb
                        )
                    """, (
                        str(uuid.uuid4()), 
                        datetime.now(),
                        booking.booked_by_client_id,
                        booking.public_offering_id,
                        json.dumps({
                            'booked_by_client_id': booking.booked_by_client_id,
                            'public_offering_id': booking.public_offering_id,
                            'booked_for_client_id': booking.booked_for_client_id
                        })
                    ))
                    
                    conn.commit()
                    logger.info(f"Successfully added booking for client {booking.booked_by_client_id}")
                    return True
                    
        except (psycopg2.Error, ValueError) as e:
            logger.error(f"Error adding booking: {str(e)}")
            return False
    
    def get_booking(self, booked_by_client_id: str, public_offering_id: str) -> Optional[Booking]:
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT booked_by_client_id, public_offering_id, booked_for_client_id
                        FROM bookings
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booked_by_client_id, public_offering_id))
                    
                    result = cur.fetchone()
                    if result:
                        return Booking(
                            booked_by_client_id=result['booked_by_client_id'],
                            public_offering_id=result['public_offering_id'],
                            booked_for_client_id=result['booked_for_client_id']
                        )
                    return None
                    
        except psycopg2.Error as e:
            logger.error(f"Error retrieving booking: {str(e)}")
            return None

    def remove_booking(self, booked_by_client_id: str, public_offering_id: str) -> bool:
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # First get the existing booking for audit log
                    cur.execute("""
                        SELECT booked_for_client_id
                        FROM bookings
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booked_by_client_id, public_offering_id))
                    
                    existing_booking = cur.fetchone()
                    if not existing_booking:
                        logger.warning(f"No booking found to remove for client {booked_by_client_id}")
                        return False
                    
                    # Delete the booking
                    cur.execute("""
                        DELETE FROM bookings
                        WHERE booked_by_client_id = %s AND public_offering_id = %s
                    """, (booked_by_client_id, public_offering_id))
                    
                    # Create audit log entry
                    cur.execute("""
                        INSERT INTO audit_logs (
                            log_id, timestamp, table_name, actor_id, action_type, 
                            target_table, record_id, old_value
                        )
                        VALUES (
                            %s, %s, 'bookings', %s, 'DELETE', 'bookings', %s,
                            %s::jsonb
                        )
                    """, (
                        str(uuid.uuid4()),
                        datetime.now(),
                        booked_by_client_id,
                        public_offering_id,
                        json.dumps({
                            'booked_by_client_id': booked_by_client_id,
                            'public_offering_id': public_offering_id,
                            'booked_for_client_id': existing_booking[0]
                        })
                    ))
                    
                    conn.commit()
                    logger.info(f"Successfully removed booking for client {booked_by_client_id}")
                    return True
                    
        except psycopg2.Error as e:
            logger.error(f"Error removing booking: {str(e)}")
            return False

if __name__ == "__main__":
    # Example usage and testing
    try:
        # Get the booking catalog instance
        booking_catalog = BookingCatalog.get_instance()
        
        # Create a test booking
        test_booking = Booking(
            booked_by_client_id=str(uuid.uuid4()),
            public_offering_id=str(uuid.uuid4()),
            booked_for_client_id=str(uuid.uuid4())
        )
        
        # Try to add the booking
        success = booking_catalog.add_booking(test_booking)
        print(f"Booking added successfully: {success}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")