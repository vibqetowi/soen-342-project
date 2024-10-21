from datetime import datetime, timedelta
from System import generate_id  # Assuming generate_id is a function to create unique IDs
from Offerings import OfferingCatalog

class ScheduleCatalog:
    """Catalog for managing schedules."""
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)  # Create a new instance if it doesn't exist
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Ensure __init__ is only called once
            self._initialized = True
            self.schedules_by_id = {}  # Hashtable to store schedules by ID
            self.schedules_by_owner = {}  # Hashtable to store schedules by owner ID

    def create_schedule(self, schedule_owner_id):
        """Creates a new schedule and adds it to the catalog."""
        new_id = generate_id()  # Using the system's generate_id method
        schedule = _Schedule(new_id, schedule_owner_id)

        # Store the schedule by its ID
        self.schedules_by_id[new_id] = schedule

        # Store the schedule by its owner's ID
        if schedule_owner_id not in self.schedules_by_owner:
            self.schedules_by_owner[schedule_owner_id] = []
        self.schedules_by_owner[schedule_owner_id].append(schedule)

        return schedule

    def get_schedule(self, schedule_id):
        """Retrieves a schedule by its ID."""
        return self.schedules_by_id.get(schedule_id, None)

    def get_schedules_by_owner(self, schedule_owner_id):
        """Retrieves all schedules for a specific owner ID."""
        return self.schedules_by_owner.get(schedule_owner_id, [])

class _Schedule:
    """Private class representing a schedule."""
    def __init__(self, schedule_id, schedule_owner_id):
        self.schedule_id = schedule_id
        self.schedule_owner_id = schedule_owner_id  # Owner can be a client, a branch, or an instructor
        self.time_slots = {}  # Hashtable to store time slots by start time
        self.generate_time_slots()  # Automatically generate time slots upon creation

    def generate_time_slots(self):
        """Generates time slots for the next week in 30-minute increments."""
        today = datetime.now()
        end_date = today + timedelta(days=7)
        current_time = today.replace(hour=0, minute=0, second=0, microsecond=0)

        while current_time < end_date:
            self.add_time_slot(current_time, current_time + timedelta(minutes=30))
            current_time += timedelta(minutes=30)

        self.delete_old_time_slots()  # Remove time slots older than today

    def add_time_slot(self, start_time, end_time):
        """Adds a time slot to the schedule."""
        time_slot = _TimeSlot(start_time, end_time)
        self.time_slots[start_time] = time_slot  # Use start time as the key

    def delete_old_time_slots(self):
        """Deletes time slots older than today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.time_slots = {k: v for k, v in self.time_slots.items() if v.start_time >= today}

    def get_available_slots(self):
        """Returns a list of available time slots."""
        return [slot for slot in self.time_slots.values() if not slot.is_reserved]

    def __repr__(self):
        return f"Schedule({self.schedule_id}) for Owner({self.schedule_owner_id})"

class _TimeSlot:
    """Private class representing a time slot."""
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.is_reserved = False

    def reserve(self):
        """Reserves the time slot."""
        self.is_reserved = True

    def cancel_reservation(self):
        """Cancels the reservation for the time slot."""
        self.is_reserved = False

    def __repr__(self):
        return f"TimeSlot({self.start_time} - {self.end_time}, Reserved: {self.is_reserved})"