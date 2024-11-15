from singleton_decorator import singleton
from sqlalchemy.orm import Session
from Database import SessionLocal
from Models import Booking
from utils import generate_id

@singleton
class BookingCatalog:
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()

    def add_booking(self, booked_by_client_id, public_offering_id, booked_for_client_ids):
        """Add a new booking to the database."""
        booking_id = generate_id()
        for client_id in booked_for_client_ids:
            booking = Booking(
                booking_id=booking_id,
                booked_by_client_id=booked_by_client_id,
                public_offering_id=public_offering_id,
                booked_for_client_id=client_id
            )
            self.session.add(booking)
        self.session.commit()

    def get_booking_by_id(self, booking_id):
        """Retrieve a booking by ID."""
        return self.session.query(Booking).filter_by(booking_id=booking_id).first()

    def remove_booking(self, booking_id):
        """Remove a booking by ID."""
        booking = self.get_booking_by_id(booking_id)
        if booking:
            self.session.delete(booking)
            self.session.commit()

    def get_all_bookings_for_client(self, client_id):
        """Retrieve all bookings for a specific client."""
        return self.session.query(Booking).filter_by(booked_for_client_id=client_id).all()

    def get_all_bookings_by_client(self, client_id):
        """Retrieve all bookings created by a specific client."""
        return self.session.query(Booking).filter_by(booked_by_client_id=client_id).all()
