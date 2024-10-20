class TimeSlot:
    def __init__(self, time_slot_id, start_time, end_time):
        self.time_slot_id = time_slot_id
        self.start_time = start_time
        self.end_time = end_time
        self.is_reserved = False

    def reserve(self):
        self.is_reserved = True

    def cancel_reservation(self):
        self.is_reserved = False

    def __repr__(self):
        return f"TimeSlot({self.time_slot_id}, {self.start_time} - {self.end_time}, Reserved: {self.is_reserved})"

class ScheduleCatalog:
    def __init__(self):
        self.schedules = {}  # This will serve as the hashtable (dictionary)
        self.current_id = 0  # To generate unique IDs

    def _generate_id(self):
        """Generates a unique schedule ID"""
        self.current_id += 1
        return self.current_id

    def create_schedule(self, schedule_owner_id):
        """Creates a new schedule and adds it to the catalog"""
        new_id = self._generate_id()
        schedule = Schedule(new_id, schedule_owner_id)
        self.schedules[new_id] = schedule
        return schedule

    def get_schedule(self, schedule_id):
        """Retrieves a schedule by its ID"""
        return self.schedules.get(schedule_id, None)

class Schedule:
    def __init__(self, schedule_id, schedule_owner_id):
        self.schedule_id = schedule_id
        self.schedule_owner_id = schedule_owner_id #owner can be a client, a branch or an instructor 
        self.time_slots = []

    def add_time_slot(self, time_slot):
        self.time_slots.append(time_slot)

    def get_available_slots(self):
        return [slot for slot in self.time_slots if not slot.is_reserved]

    def __repr__(self):
        return f"Schedule({self.schedule_id}) for Owner({self.schedule_owner_id .name})"
