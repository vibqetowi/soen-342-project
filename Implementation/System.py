import bcrypt
from singleton_decorator import singleton
from utils import generate_id
from Database import SessionLocal
from Users import UserCatalog
from Offerings import OfferingCatalog
from Bookings import BookingCatalog
from Location import LocationCatalog
from Scheduling import ScheduleCatalog
from Models import Client
from sqlalchemy.exc import SQLAlchemyError


def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(provided_password: str, stored_hashed_password: bytes) -> bool:
    """Checks if the provided password matches the stored hashed password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password)


@singleton
class System:
    
    def __init__(self):
        # Set up a session for database transactions
        self.session = SessionLocal()

        # Initialize all catalog instances with the session
        self.user_catalog = UserCatalog(self.session)
        self.offering_catalog = OfferingCatalog(self.session)
        self.booking_catalog = BookingCatalog(self.session)
        self.location_catalog = LocationCatalog(self.session)
        self.schedule_catalog = ScheduleCatalog(self.session)

    def close_session(self):
        """Close the session to free up resources."""
        self.session.close()

    # Administrator actions
    def create_offering(self, lesson_type, mode, capacity):
        """Create a new offering through the OfferingCatalog."""
        try:
            offering = self.offering_catalog.create_offering(
                instructor_id=None,
                lesson_type=lesson_type,
                mode=mode,
                capacity=capacity
            )
            self.session.commit()
            return offering
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error creating offering: {e}")
            return None

    def delete_user(self, user_id):
        """Delete a user from the UserCatalog."""
        try:
            result = self.user_catalog.remove_user(user_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error deleting user: {e}")
            return None

    def edit_user(self, user_id, **kwargs):
        """Edit user information."""
        try:
            result = self.user_catalog.edit_user(user_id, **kwargs)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error editing user: {e}")
            return None

    def delete_booking(self, booking_id):
        """Delete a booking from the BookingCatalog."""
        try:
            result = self.booking_catalog.remove_booking(booking_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error deleting booking: {e}")
            return None

    def edit_booking(self, booking_id, **kwargs):
        """Edit booking information."""
        try:
            result = self.booking_catalog.edit_booking(booking_id, **kwargs)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error editing booking: {e}")
            return None

    def delete_offering(self, offering_id):
        """Delete an offering from the OfferingCatalog."""
        try:
            result = self.offering_catalog.delete_offering(offering_id)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error deleting offering: {e}")
            return None

    def edit_offering(self, offering_id, **kwargs):
        """Edit offering information."""
        try:
            result = self.offering_catalog.edit_offering(offering_id, **kwargs)
            self.session.commit()
            return result
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error editing offering: {e}")
            return None

    def register_client(self, email, password, **kwargs):
        """Register a new client."""
        try:
            if self.user_catalog.get_user_by_email(email):
                print("Email already in use.")
                return None
            hashed_password = hash_password(password)
            client_id = generate_id()
            client = Client(
                client_id=client_id,
                email=email,
                password=hashed_password,
                schedule_catalog=self.schedule_catalog,
                **kwargs
            )
            self.user_catalog.add_user(client)
            self.session.commit()
            return client
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error registering client: {e}")
            return None

    def login(self, email, password):
        """Authenticate a user based on email and password."""
        user = self.user_catalog.get_user_by_email(email)
        if user and check_password(password, user.password):
            return user
        print("Login failed: invalid credentials.")
        return None

    def search_public_offerings(self, search_query):
        """Search for public offerings based on a query."""
        return [
            offering for offering in self.offering_catalog.get_all_public_offerings()
            if search_query.lower() in offering.lesson_type.lower()
        ]


class Administrator:
    def __init__(self, admin_id, email, password):
        self.user_id = admin_id
        self.admin_id = admin_id
        self.email = email
        self.password = password  # Should be stored as a hashed password

    # Administrator methods

    def create_offering(self, lesson_type, mode, capacity):
        """Create a new offering."""
        system = System.get_instance()
        return system.create_offering(lesson_type, mode, capacity)

    def delete_user(self, user_id):
        """Delete a user."""
        system = System.get_instance()
        return system.delete_user(user_id)

    def edit_user(self, user_id, **kwargs):
        """Edit user information."""
        system = System.get_instance()
        return system.edit_user(user_id, **kwargs)

    def delete_booking(self, booking_id):
        """Delete a booking."""
        system = System.get_instance()
        return system.delete_booking(booking_id)

    def edit_booking(self, booking_id, **kwargs):
        """Edit booking information."""
        system = System.get_instance()
        return system.edit_booking(booking_id)

    def delete_offering(self, offering_id):
        """Delete an offering."""
        system = System.get_instance()
        return system.delete_offering(offering_id)

    def edit_offering(self, offering_id, **kwargs):
        """Edit offering information."""
        system = System.get_instance()
        return system.edit_offering(offering_id)

    def __repr__(self):
        return f"Administrator(admin_id={self.admin_id}, email='{self.email}')"
