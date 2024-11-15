from datetime import datetime, timedelta
from utils import generate_id
from sqlalchemy.orm import Session
from Database import SessionLocal  # Import session management from Database.py
from Models import Schedule, TimeSlot, Client, Branch, Instructor  

class ScheduleCatalog:
    def __init__(self, session: Session):
        self.session = session

from datetime import datetime, timedelta
from utils import generate_id
from sqlalchemy.orm import Session
from Database import SessionLocal  # Import session management from Database.py
from Models import Schedule, TimeSlot, Client  

class ScheduleCatalog:
    def __init__(self, session: Session):
        self.session = session

    def create_schedule(self, owner_id, owner_type):
        # Verify the owner exists based on owner_type
        if owner_type == 'client':
            owner = self.session.query(Client).filter_by(user_id=owner_id).first()
        elif owner_type == 'branch':
            owner = self.session.query(Branch).filter_by(location_id=owner_id).first()
        elif owner_type == 'instructor':
            owner = self.session.query(Instructor).filter_by(user_id=owner_id).first()
        else:
            raise ValueError("Invalid owner type specified.")

        if not owner:
            raise ValueError(f"The specified {owner_type} does not exist in the database.")

        # Create and commit the schedule
        schedule = Schedule(
            schedule_id=generate_id(),
            schedule_owner_id=owner_id,
            schedule_owner_type=owner_type
        )
        self.session.add(schedule)
        self.session.commit()
        return schedule

    def get_schedule(self, schedule_id):
        """Retrieves a schedule by its ID."""
        return self.session.query(Schedule).filter_by(schedule_id=schedule_id).first()

    def get_schedules_by_owner(self, schedule_owner_id):
        """Retrieves all schedules for a specific owner ID."""
        return self.session.query(Schedule).filter_by(schedule_owner_id=schedule_owner_id).all()

    def generate_time_slots(self, schedule):
        """Generates time slots for the next week in 30-minute increments for a given schedule."""
        today = datetime.now()
        end_date = today + timedelta(days=7)
        current_time = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_time < end_date:
            start_time = current_time
            end_time = start_time + timedelta(minutes=30)
            time_slot = TimeSlot(
                schedule_id=schedule.schedule_id,
                start_time=start_time,
                end_time=end_time,
                is_reserved=False
            )
            self.session.add(time_slot)  # Add time slot to session
            current_time = end_time
        
        self.session.commit()  # Commit all new time slots to the database



    def get_schedule(self, schedule_id):
        """Retrieves a schedule by its ID."""
        return self.session.query(Schedule).filter_by(schedule_id=schedule_id).first()

    def get_schedules_by_owner(self, schedule_owner_id):
        """Retrieves all schedules for a specific owner ID."""
        return self.session.query(Schedule).filter_by(schedule_owner_id=schedule_owner_id).all()

    def generate_time_slots(self, schedule):
        """Generates time slots for the next week in 30-minute increments for a given schedule."""
        today = datetime.now()
        end_date = today + timedelta(days=7)
        current_time = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_time < end_date:
            start_time = current_time
            end_time = start_time + timedelta(minutes=30)
            time_slot = TimeSlot(
                schedule_id=schedule.schedule_id,
                start_time=start_time,
                end_time=end_time,
                is_reserved=False
            )
            self.session.add(time_slot)  # Add time slot to session
            current_time = end_time
        
        self.session.commit()  # Commit all new time slots to the database

