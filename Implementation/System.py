import bcrypt
from singleton_decorator import singleton
from utils import generate_id
from Database import SessionLocal
from Users import UserCatalog
from Offerings import OfferingCatalog
from Bookings import BookingCatalog
from Location import LocationCatalog
from Scheduling import ScheduleCatalog
from Models import Client, Administrator, Instructor
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
        self.session = SessionLocal()

        self.user_catalog = UserCatalog(self.session)
        self.offering_catalog = OfferingCatalog(self.session)
        self.booking_catalog = BookingCatalog(self.session)
        self.location_catalog = LocationCatalog(self.session)
        self.schedule_catalog = ScheduleCatalog(self.session)

    def close_session(self):
        """Close the session to free up resources."""
        self.session.close()

    # Registration actions
    def register_client(self, email, password, **kwargs):
        """Register a new client."""
        try:
            if self.user_catalog.get_user_by_email(email):
                print("Email already in use.")
                return None
            hashed_password = hash_password(password)
            client_id = generate_id()
            client = Client(
                user_id=client_id,
                email=email,
                hashed_password=hashed_password,
                **kwargs
            )
            self.session.add(client)
            self.session.commit()
            return client
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error registering client: {e}")
            return None

    def register_instructor(self, email, password, **kwargs):
        """Register a new instructor."""
        try:
            if self.user_catalog.get_user_by_email(email):
                print("Email already in use.")
                return None
            hashed_password = hash_password(password)
            instructor_id = generate_id()
            instructor = Instructor(
                user_id=instructor_id,
                email=email,
                hashed_password=hashed_password,
                **kwargs
            )
            self.session.add(instructor)
            self.session.commit()
            return instructor
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error registering instructor: {e}")
            return None

    def register_administrator(self, email, password, **kwargs):
        """Register a new administrator."""
        try:
            if self.user_catalog.get_user_by_email(email):
                print("Email already in use.")
                return None
            hashed_password = hash_password(password)
            admin_id = generate_id()
            admin = Administrator(
                user_id=admin_id,
                email=email,
                hashed_password=hashed_password,
                **kwargs
            )
            self.session.add(admin)
            self.session.commit()
            return admin
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error registering administrator: {e}")
            return None


#To prevent circular imports, Administrator was added to the System.py as it relies heavily on System methods
class Administrator:
    def __init__(self, admin_id, email, password):
        self.user_id = admin_id
        self.admin_id = admin_id
        self.email = email
        self.password = password  


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
