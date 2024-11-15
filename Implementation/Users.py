from utils import generate_id
from singleton_decorator import singleton
from Bookings import Booking
from sqlalchemy.orm import Session
from Database import SessionLocal 
from Models import Client, Instructor, Administrator


@singleton
class UserCatalog:

    def __init__(self, session: Session):
        self.session = session
        self.users = {}  # Dictionary to store users by their IDs
        self.email_to_user = {}  # Dictionary to map emails to user instances for login

    def add_user(self, user):
        """Add a user to the catalog and database."""
        self.session.add(user)
        self.session.commit()
        self.users[user.user_id] = user
        self.email_to_user[user.email] = user

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.session.query(Client).filter_by(user_id=user_id).first() or \
                self.session.query(Instructor).filter_by(user_id=user_id).first()

    def get_user_by_email(self, email):
        """Retrieve a user by their email."""
        return self.session.query(Client).filter_by(email=email).first() or \
                self.session.query(Instructor).filter_by(email=email).first()

    def remove_user(self, user_id):
        """Remove a user from the catalog and database."""
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            self.users.pop(user_id, None)
            self.email_to_user.pop(user.email, None)

    def login(self, email, password):
        """Authenticate a user based on email and password."""
        user = self.get_user_by_email(email)
        if user and user.password == password:
            return user
        return None
    
class Instructor:
    def __init__(self, instructor_id, name, phone, specialization, email, password, schedule_catalog):
        self.user_id = instructor_id
        self.name = name
        self.phone = phone
        self.specialization = specialization
        self.email = email
        self.password = password
        # Initialize schedule in the database
        self.schedule = schedule_catalog.create_schedule(instructor_id)
        self.available_cities = []  # May need to be managed with database records

    def create_offering(self, offering_catalog, lesson_type, mode, capacity):
        """Create an offering and add it to the database."""
        offering = offering_catalog.create_offering(
            instructor_id=self.user_id,
            lesson_type=lesson_type,
            mode=mode,
            capacity=capacity
        )
        return offering

    def create_public_offering(self, offering_catalog, offering_id, max_clients):
        """Create a public offering and add it to the database."""
        public_offering = offering_catalog.create_public_offering(offering_id, max_clients)
        return public_offering

    def set_availability(self, city_id):
        """Add a city to the instructor's availability in the database."""
        # This should ideally add a record in an InstructorCityAvailability table.
        if city_id not in self.available_cities:
            self.available_cities.append(city_id)  # Placeholder until database is set up

    def __repr__(self):
        return (f"Instructor(instructor_id={self.user_id}, name='{self.name}', "
                f"specialization='{self.specialization}', email='{self.email}')")
        
class Client:
    def __init__(self, client_id, email, password, schedule_catalog, age=None, guardian_id=None):
        self.user_id = client_id
        self.email = email
        self.password = password  # Store hashed password
        self.age = age
        self.guardian_id = guardian_id
        # Initialize schedule in the database
        self.schedule = schedule_catalog.create_schedule(client_id)
        self.bookings = []  # This will interact with the BookingCatalog

    def create_booking(self, booking_catalog, public_offering_id, booked_for_client_ids):
        """Create a booking and add it to the database."""
        booking_id = generate_id()
        booking = Booking(
            booking_id=booking_id,
            booked_by_client_id=self.user_id,
            public_offering_id=public_offering_id,
            booked_for_client_ids=booked_for_client_ids
        )
        booking_catalog.add_booking(booking)
        self.bookings.append(booking_id)
        return booking

    def cancel_booking(self, booking_catalog, booking_id):
        """Cancel a booking."""
        booking = booking_catalog.get_booking_by_id(booking_id)
        if booking and booking.booked_by_client_id == self.user_id:
            booking_catalog.remove_booking(booking_id)
            self.bookings.remove(booking_id)
            return True
        return False

    def make_booking(self, system, search_query):
        """Make a booking based on a search query."""
        public_offerings = system.search_public_offerings(search_query)
        if not public_offerings:
            print("No offerings found.")
            return None

        # Assume selection and booking are handled interactively or via another method.
        # Database logic to persist the booking will be similar to create_booking.

    def cancel_booking(self, system, offering_id):
        """Cancel a booking for a given offering in the database."""
        offering = system.offering_catalog.get_public_offering(offering_id)
        if not offering:
            print("Offering not found.")
            return False

        # Check if booking exists and perform database delete operations as needed.

    def notify_cancellation(self, offering_id):
        """Notify the client about a booking cancellation."""
        print(f"Notification: A booking for offering {offering_id} has been canceled.")

    def __repr__(self):
        return (f"Client(client_id={self.user_id}, age={self.age}, "
                f"email='{self.email}', guardian_id={self.guardian_id})")
