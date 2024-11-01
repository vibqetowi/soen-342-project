class Booking:
    def __init__(self, booking_id, booked_by_client_id, public_offering_id, booked_for_client_ids):
        self.booking_id = booking_id
        self.booked_by_client_id = booked_by_client_id
        self.public_offering_id = public_offering_id
        self.booked_for_client_ids = booked_for_client_ids  # List of client IDs

    def __repr__(self):
        return (f"Booking(booking_id={self.booking_id}, "
                f"booked_by_client_id={self.booked_by_client_id}, "
                f"public_offering_id={self.public_offering_id}, "
                f"booked_for_client_ids={self.booked_for_client_ids})")

class BookingCatalog:
    __instance = None

    def __init__(self):
        if BookingCatalog.__instance is not None:
            raise Exception("Singleton Class")
        else:
            BookingCatalog.__instance = self
            self.bookings = []

    @staticmethod
    def get_instance():
        if BookingCatalog.__instance is None:
            BookingCatalog()
        return BookingCatalog.__instance

    def add_booking(self, booking):
        self.bookings.append(booking)

    def get_booking_by_id(self, get_booking_id):
        for booking in self.bookings:
            if booking.booking_id == get_booking_id:
                return booking
        return None

    def remove_booking(self, booking_id_to_remove):
        self.bookings = [b for b in self.bookings if b.booking_id != booking_id_to_remove]
