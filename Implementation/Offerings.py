from System import generate_id
from Bookings import BookingCatalog

class OfferingCatalog:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OfferingCatalog, cls).__new__(cls)
            cls._instance._offerings = {}  # Key: offering_id, Value: Offering instance
            cls._instance._public_offerings = {}  # Key: public_offering_id, Value: PublicOffering instance
        return cls._instance

    def create_offering(self, instructor_id, lesson_type, mode, capacity):
        offering_id = generate_id()
        offering = Offering(offering_id, instructor_id, lesson_type, mode, capacity)
        self._offerings[offering_id] = offering
        return offering

    def get_offering(self, offering_id):
        return self._offerings.get(offering_id)

    def create_public_offering(self, offering_id, max_clients):
        offering = self.get_offering(offering_id)
        if not offering:
            raise ValueError("Offering not found.")
        public_offering_id = generate_id()
        public_offering = PublicOffering(public_offering_id, offering, max_clients)
        self._public_offerings[public_offering_id] = public_offering
        return public_offering

    def get_public_offering(self, public_offering_id):
        return self._public_offerings.get(public_offering_id)

    def get_all_public_offerings(self):
        return list(self._public_offerings.values())
    
#TODO: add methods to remove and list or modify offerings.

class Offering:
    def __init__(self, offering_id, instructor_id, lesson_type, mode, capacity):
        self.offering_id = offering_id
        self.instructor_id = instructor_id
        self.lesson_type = lesson_type
        self.mode = mode  # group or solo lesson
        self.capacity = capacity

    def __repr__(self):
        return (f"Offering(offering_id={self.offering_id}, instructor_id={self.instructor_id}, "
                f"lesson_type='{self.lesson_type}', mode='{self.mode}', capacity={self.capacity})")

class PublicOffering(Offering):
    def __init__(self, public_offering_id, offering, max_clients):
        super().__init__(offering.offering_id, offering.instructor_id, offering.lesson_type, offering.mode, offering.capacity)
        self.public_offering_id = public_offering_id
        self.max_clients = max_clients
        self.instructor_id_list = [self.instructor_id]  # In case multiple instructors can be associated
        self.associated_booking_id_list = []  # List of booking IDs
        self.reserved_timeslot_id_list = []  # List of timeslot IDs (start_time)

    def add_booking(self, booking_id):
        self.associated_booking_id_list.append(booking_id)

    def reserve_timeslot(self, timeslot):
        self.reserved_timeslot_id_list.append(timeslot.start_time)
        timeslot.reserve()

    def __repr__(self):
        return (f"PublicOffering(public_offering_id={self.public_offering_id}, offering_id={self.offering_id}, "
                f"max_clients={self.max_clients}, instructor_id_list={self.instructor_id_list})")
    
    def get_client_ids(self):
        """Get all client IDs associated with this offering."""
        client_ids = []
        for booking_id in self.associated_booking_id_list:
            booking = BookingCatalog.get_instance().get_booking_by_id(booking_id)
            if booking:
                client_ids.extend(booking.booked_for_client_ids)
        return client_ids

    def adjust_capacity(self, amount):
        """Adjust the capacity of the offering."""
        self.max_clients += amount

    def get_client_ids(self):
        """Get all client IDs associated with this offering."""
        client_ids = []
        for booking_id in self.associated_booking_id_list:
            booking = BookingCatalog.get_instance().get_booking_by_id(booking_id)
            if booking:
                client_ids.extend(booking.booked_for_client_ids)
        return client_ids

    def adjust_capacity(self, amount):
        """Adjust the capacity of the offering."""
        self.max_clients += amount
