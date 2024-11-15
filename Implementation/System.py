import bcrypt
from singleton_decorator import singleton
from utils import generate_id
from Users import UserCatalog, Client
from Offerings import OfferingCatalog
from Bookings import BookingCatalog
from Location import LocationCatalog
from Scheduling import ScheduleCatalog



def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(provided_password: str, stored_hashed_password: bytes) -> bool:
    """Checks if the provided password matches the stored hashed password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password)

@singleton
class System:

    def __init__(self):

        # Initialize the catalogs
        self.user_catalog = UserCatalog()
        self.offering_catalog = OfferingCatalog()
        self.booking_catalog = BookingCatalog.get_instance()
        self.location_catalog = LocationCatalog()
        self.schedule_catalog = ScheduleCatalog()

    # System methods corresponding to Administrator actions

    def create_offering(self, lesson_type, mode, capacity):
        """Create a new offering through the OfferingCatalog."""
        # Assuming admin-created offerings have instructor_id = None
        offering = self.offering_catalog.create_offering(
            instructor_id=None,
            lesson_type=lesson_type,
            mode=mode,
            capacity=capacity
        )
        return offering

    def delete_user(self, user_id):
        """Delete a user from the UserCatalog."""
        user = self.user_catalog.get_user_by_id(user_id)
        if user:
            self.user_catalog.remove_user(user_id)
            return True
        return False

    def edit_user(self, user_id, **kwargs):
        """Edit user information."""
        user = self.user_catalog.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return True
        return False

    def delete_booking(self, booking_id):
        """Delete a booking from the BookingCatalog."""
        booking = self.booking_catalog.get_booking_by_id(booking_id)
        if booking:
            self.booking_catalog.remove_booking(booking_id)
            return True
        return False

    def edit_booking(self, booking_id, **kwargs):
        """Edit booking information."""
        booking = self.booking_catalog.get_booking_by_id(booking_id)
        if booking:
            for key, value in kwargs.items():
                if hasattr(booking, key):
                    setattr(booking, key, value)
            return True
        return False

    def delete_offering(self, offering_id):
        """Delete an offering from the OfferingCatalog."""
        offering = self.offering_catalog.get_offering(offering_id)
        if offering:
            self.offering_catalog.delete_offering(offering_id)
            return True
        return False

    def edit_offering(self, offering_id, **kwargs):
        """Edit offering information."""
        offering = self.offering_catalog.get_offering(offering_id)
        if offering:
            for key, value in kwargs.items():
                if hasattr(offering, key):
                    setattr(offering, key, value)
            return True
        return False

    def register_client(self, email, password, **kwargs):
        """Register a new client."""
        if self.user_catalog.get_user_by_email(email):
            return None  # Email already in use
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
        return client

    def login(self, email, password):
        """Authenticate a user based on email and password."""
        user = self.user_catalog.get_user_by_email(email)
        if user and check_password(password, user.password):
            return user
        return None
    
    def search_public_offerings(self, search_query):
        """Search for public offerings based on a query."""
        # For simplicity, search by lesson type
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
        return system.edit_booking(booking_id, **kwargs)

    def delete_offering(self, offering_id):
        """Delete an offering."""
        system = System.get_instance()
        return system.delete_offering(offering_id)

    def edit_offering(self, offering_id, **kwargs):
        """Edit offering information."""
        system = System.get_instance()
        return system.edit_offering(offering_id, **kwargs)

    def __repr__(self):
        return f"Administrator(admin_id={self.admin_id}, email='{self.email}')"