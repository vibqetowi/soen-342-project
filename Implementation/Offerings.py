from utils import generate_id
from singleton_decorator import singleton
from sqlalchemy.orm import Session
from Database import SessionLocal
from Models import Offering, PublicOffering, Booking  # Assuming Booking is used for associated bookings

@singleton
class OfferingCatalog:
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()

    def create_offering(self, instructor_id, lesson_type, mode, capacity):
        """Creates a new offering and stores it in the database."""
        offering_id = generate_id()
        offering = Offering(
            offering_id=offering_id,
            instructor_id=instructor_id,
            lesson_type=lesson_type,
            mode=mode,
            capacity=capacity
        )
        self.session.add(offering)
        self.session.commit()
        return offering

    def get_offering(self, offering_id):
        """Retrieves an offering from the database by ID."""
        return self.session.query(Offering).filter_by(offering_id=offering_id).first()

    def create_public_offering(self, offering_id, max_clients):
        """Creates a new public offering based on an existing offering."""
        offering = self.get_offering(offering_id)
        if not offering:
            raise ValueError("Offering not found.")

        public_offering_id = generate_id()
        public_offering = PublicOffering(
            public_offering_id=public_offering_id,
            offering_id=offering_id,
            max_clients=max_clients
        )
        self.session.add(public_offering)
        self.session.commit()
        return public_offering

    def get_public_offering(self, public_offering_id):
        """Retrieves a public offering from the database by ID."""
        return self.session.query(PublicOffering).filter_by(public_offering_id=public_offering_id).first()

    def get_all_public_offerings(self):
        """Retrieves all public offerings from the database."""
        return self.session.query(PublicOffering).all()

class PublicOfferingService:
    def __init__(self, public_offering_id, session=None):
        self.session = session or SessionLocal()
        self.public_offering = self.session.query(PublicOffering).filter_by(public_offering_id=public_offering_id).first()

    def add_booking(self, booking_id):
        """Add a booking to the public offering."""
        booking = self.session.query(Booking).filter_by(booking_id=booking_id).first()
        if booking and booking.public_offering_id == self.public_offering.public_offering_id:
            self.public_offering.bookings.append(booking)
            self.session.commit()

    def reserve_timeslot(self, timeslot):
        """Reserve a time slot for this offering."""
        if timeslot.is_reserved:
            raise ValueError("Time slot already reserved.")
        timeslot.is_reserved = True
        timeslot.reserved_by_public_offering_id = self.public_offering.public_offering_id
        self.session.commit()

    def get_client_ids(self):
        """Get all client IDs associated with this public offering."""
        return [booking.booked_for_client_id for booking in self.public_offering.bookings]

    def adjust_capacity(self, amount):
        """Adjust the capacity of the public offering."""
        self.public_offering.max_clients += amount
        self.session.commit()
