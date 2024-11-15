from utils import generate_id
from singleton_decorator import singleton
from Bookings import Booking

@singleton
class UserCatalog:

    def __init__(self):
        self.users = {}  # Dictionary to store users by their IDs
        self.email_to_user = {}  # Dictionary to map emails to user instances for login

    def add_user(self, user):
        """Add a user to the catalog."""
        self.users[user.user_id] = user
        self.email_to_user[user.email] = user

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.users.get(user_id)

    def get_user_by_email(self, email):
        """Retrieve a user by their email."""
        return self.email_to_user.get(email)

    def remove_user(self, user_id):
        """Remove a user from the catalog."""
        user = self.users.pop(user_id, None)
        if user:
            self.email_to_user.pop(user.email, None)

    def login(self, email, password):
        """Authenticate a user based on email and password."""
        user = self.get_user_by_email(email)
        if user and user.password == password:
            return user
        return None

    def register_client(self, age, email, password, schedule_catalog, guardian_id=None):
        """Register a new client."""
        client_id = generate_id()
        client = Client(
            client_id=client_id,
            age=age,
            email=email,
            password=password,
            schedule_catalog=schedule_catalog,
            guardian_id=guardian_id
        )
        self.add_user(client)
        return client

    def register_instructor(self, name, phone, specialization, email, password, schedule_catalog):
        """Register a new instructor."""
        instructor_id = generate_id()
        instructor = Instructor(
            instructor_id=instructor_id,
            name=name,
            phone=phone,
            specialization=specialization,
            email=email,
            password=password,
            schedule_catalog=schedule_catalog
        )
        self.add_user(instructor)
        return instructor

class Instructor:
    def __init__(self, instructor_id, name, phone, specialization, email, password, schedule_catalog):
        self.user_id = instructor_id  # Using 'user_id' for consistency
        self.instructor_id = instructor_id
        self.name = name
        self.phone = phone
        self.specialization = specialization
        self.email = email
        self.password = password
        self.schedule = schedule_catalog.create_schedule(instructor_id)
        self.available_cities = []  # List of city IDs where the instructor is available

    def create_offering(self, offering_catalog, lesson_type, mode, capacity):
        offering = offering_catalog.create_offering(
            instructor_id=self.instructor_id,
            lesson_type=lesson_type,
            mode=mode,
            capacity=capacity
        )
        return offering

    def create_public_offering(self, offering_catalog, offering_id, max_clients):
        public_offering = offering_catalog.create_public_offering(offering_id, max_clients)
        return public_offering

    def set_availability(self, city_id):
        """Add a city to the instructor's availability."""
        if city_id not in self.available_cities:
            self.available_cities.append(city_id)

    def __repr__(self):
        return (f"Instructor(instructor_id={self.instructor_id}, name='{self.name}', "
                f"specialization='{self.specialization}', email='{self.email}')")
        
class Client:
    def __init__(self, client_id, email, password, schedule_catalog, age=None, guardian_id=None):
        self.user_id = client_id
        self.client_id = client_id
        self.email = email
        self.password = password  # Store hashed password
        self.age = age
        self.guardian_id = guardian_id
        self.schedule = schedule_catalog.create_schedule(client_id)
        self.bookings = []

    def create_booking(self, booking_catalog, booking_id, public_offering_id, booked_for_client_ids):
        """Create a booking and add it to the booking catalog."""
        booking = Booking(
            booking_id=booking_id,
            booked_by_client_id=self.client_id,
            public_offering_id=public_offering_id,
            booked_for_client_ids=booked_for_client_ids
        )
        booking_catalog.add_booking(booking)
        self.bookings.append(booking_id)
        return booking

    def cancel_booking(self, booking_catalog, booking_id):
        """Cancel a booking."""
        booking = booking_catalog.get_booking_by_id(booking_id)
        if booking and booking.booked_by_client_id == self.client_id:
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

        # Simulate client selecting an offering
        print("Available Offerings:")
        for idx, offering in enumerate(public_offerings):
            print(f"{idx + 1}. {offering}")

        selection = int(input("Select an offering by number: ")) - 1
        if selection < 0 or selection >= len(public_offerings):
            print("Invalid selection.")
            return None

        selected_offering = public_offerings[selection]
        if selected_offering.max_clients <= len(selected_offering.associated_booking_id_list):
            print("Offering is full.")
            return None

        # Check for schedule conflicts
        client_schedule = self.schedule
        offering_timeslots = selected_offering.reserved_timeslot_id_list
        client_timeslots = [ts.start_time for ts in client_schedule.get_reserved_slots()]

        conflict = False
        for ts in offering_timeslots:
            if ts in client_timeslots:
                conflict = True
                break

        if conflict:
            print("Schedule conflict detected.")
            return None

        # Create booking
        booking_id = generate_id()
        booking = Booking(
            booking_id=booking_id,
            booked_by_client_id=self.client_id,
            public_offering_id=selected_offering.public_offering_id,
            booked_for_client_ids=[self.client_id]
        )
        system.booking_catalog.add_booking(booking)
        self.bookings.append(booking_id)
        selected_offering.add_booking(booking_id)
        client_schedule.add_reserved_slots(offering_timeslots)
        print("Booking successful.")
        return booking

    def cancel_booking(self, system, offering_id):
        """Cancel a booking for a given offering."""
        offering = system.offering_catalog.get_public_offering(offering_id)
        if not offering:
            print("Offering not found.")
            return False

        if self.client_id not in offering.get_client_ids():
            print("You do not have a booking for this offering.")
            return False

        # Remove booking
        booking_id = None
        for b_id in offering.associated_booking_id_list:
            booking = system.booking_catalog.get_booking_by_id(b_id)
            if booking and self.client_id in booking.booked_for_client_ids:
                booking_id = b_id
                break

        if booking_id:
            offering.associated_booking_id_list.remove(booking_id)
            system.booking_catalog.remove_booking(booking_id)
            self.bookings.remove(booking_id)
            offering.adjust_capacity(-1)
            # Remove reserved time slots from client's schedule
            self.schedule.cancel_reserved_slots(offering.reserved_timeslot_id_list)
            print("Booking canceled successfully.")

            # Notify other clients (simplified)
            for client_id in offering.get_client_ids():
                other_client = system.user_catalog.get_user_by_id(client_id)
                if other_client:
                    other_client.notify_cancellation(offering_id)

            return True
        else:
            print("Booking not found.")
            return False

    def notify_cancellation(self, offering_id):
        """Notify the client about a cancellation."""
        print(f"Notification: A booking for offering {offering_id} has been canceled.")

    def __repr__(self):
        return (f"Client(client_id={self.client_id}, age={self.age}, "
                f"email='{self.email}', guardian_id={self.guardian_id})")
