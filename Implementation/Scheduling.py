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


class Schedule:
    def __init__(self, schedule_id, branch):
        self.schedule_id = schedule_id
        self.branch = branch
        self.time_slots = []
        branch.add_schedule(self)

    def add_time_slot(self, time_slot):
        self.time_slots.append(time_slot)

    def get_available_slots(self):
        return [slot for slot in self.time_slots if not slot.is_reserved]

    def __repr__(self):
        return f"Schedule({self.schedule_id}) for Branch({self.branch.name})"
