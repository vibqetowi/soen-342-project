# main.py

from System import System, generate_id, Administrator  # Import System and generate_id
from Users import Instructor, Client    # Import Instructor and Client classes
from Offerings import Offering, PublicOffering  # Import Offering and PublicOffering
from Bookings import Booking            # Import Booking class
from datetime import datetime           # Import datetime for time_slot
from Location import LocationCatalog    # Import LocationCatalog

def main():
    # Initialize the system and catalogs
    system = System()
    user_catalog = system.user_catalog
    offering_catalog = system.offering_catalog
    booking_catalog = system.booking_catalog
    location_catalog = system.location_catalog
    schedule_catalog = system.schedule_catalog

    # --- Initialize Location Catalog ---
    provinces = [
        ("Ontario", ["Toronto", "Ottawa", "Hamilton"]),
        ("Quebec", ["Montreal", "Quebec City", "Laval"])
    ]

    # Create provinces and their respective cities and branches
    for province_name, cities in provinces:
        province = location_catalog.create_province(province_name)

        for city_name in cities:
            city = location_catalog.create_city(province.province_id, city_name)

            # Create branches for each city
            for branch_num in range(1, 5):  # Four branches
                branch_name = f"{city.name} Branch {branch_num}"
                branch = location_catalog.create_branch(city.city_id, branch_name, schedule_catalog)  

    # admin generation
    admin_id = generate_id()
    admin = Administrator(admin_id=admin_id, email="admin@test.com", password="adminpass")


    # ---------------------------
    # Constraint 1: Offerings are unique. Multiple offerings on the same day and time slot must be offered at a different location.
    # ---------------------------

    print("\n--- Testing Constraint 1: Unique Offerings per Location ---")

    # Create an instructor
    instructor_id = generate_id()
    instructor = Instructor(
        instructor_id=instructor_id,
        name="Jean Doe",
        phone="514-555-7890",
        specialization="Yoga",
        email="jean.doe@yoga.com",
        password="iluvyoga69",
        schedule_catalog=schedule_catalog
    )
    user_catalog.add_user(instructor)

    # Set instructor availability to Toronto and Ottawa
    toronto_city = location_catalog.get_city_by_name("Toronto")
    ottawa_city = location_catalog.get_city_by_name("Ottawa")
    instructor.set_availability(toronto_city.city_id)
    instructor.set_availability(ottawa_city.city_id)

    # Create offerings at the same time slot but different locations
    time_slot = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    location1 = toronto_city
    location2 = ottawa_city

    # Offering 1 in Toronto
    offering1 = Offering(
        offering_id=generate_id(),
        instructor_id=instructor_id,
        lesson_type="Yoga",
        mode="Group",
        capacity=10
    )
    offering1.time_slot = time_slot
    offering1.location = location1

    # Offering 2 in Ottawa
    offering2 = Offering(
        offering_id=generate_id(),
        instructor_id=instructor_id,
        lesson_type="Yoga",
        mode="Group",
        capacity=10
    )
    offering2.time_slot = time_slot
    offering2.location = location2

    # Add offerings to the catalog
    offering_catalog._offerings[offering1.offering_id] = offering1
    offering_catalog._offerings[offering2.offering_id] = offering2

    # Check for uniqueness constraint
    offerings = list(offering_catalog._offerings.values())
    conflict_exists = False
    for i in range(len(offerings)):
        for j in range(i + 1, len(offerings)):
            o1 = offerings[i]
            o2 = offerings[j]
            if o1.time_slot == o2.time_slot and o1.location == o2.location:
                conflict_exists = True
                print(f"Conflict detected between offerings {o1.offering_id} and {o2.offering_id}")
    if not conflict_exists:
        print("Constraint 1 passed: No conflicting offerings at the same location and time slot.")

    # ---------------------------
    # Constraint 2: Underage clients must have a guardian.
    # ---------------------------

    print("\n--- Testing Constraint 2: Underage Clients Must Have Guardian ---")

    # Create an underage client without a guardian
    underage_client = Client(
        client_id=generate_id(),
        email="kiddo@diddy.com",
        password="iluvepstein",
        schedule_catalog=schedule_catalog,
        age=16,
        guardian_id=None  # No guardian provided
    )
    user_catalog.add_user(underage_client)

    # Create an adult client to act as guardian
    guardian_client = Client(
        client_id=generate_id(),
        email="diddy@party.com",
        password="ihavelegalguardianship",
        schedule_catalog=schedule_catalog,
        age=30
    )
    user_catalog.add_user(guardian_client)

    underage_client_with_guardian = Client(
        client_id=generate_id(),
        email="kidboss@example.com",
        password="password123",
        schedule_catalog=schedule_catalog,
        age=17,
        guardian_id=guardian_client.client_id  # Guardian provided
    )
    user_catalog.add_user(underage_client_with_guardian)

    # Check the constraint
    clients = [underage_client, underage_client_with_guardian]
    for client in clients:
        if client.age < 18 and not client.guardian_id:
            print(f"Constraint 2 violated: Underage client {client.client_id} does not have a guardian.")
        else:
            print(f"Constraint 2 passed for client {client.client_id}.")

    # ---------------------------
    # Constraint 3: Offering's city must be in instructor's available cities.
    # ---------------------------

    print("\n--- Testing Constraint 3: Offering City in Instructor Availability ---")

    # Create an offering in a city not in the instructor's availability
    hamilton_city = location_catalog.get_city_by_name("Hamilton")

    invalid_offering = Offering(
        offering_id=generate_id(),
        instructor_id=instructor_id,
        lesson_type="Pilates",
        mode="Solo",
        capacity=5
    )
    invalid_offering.time_slot = time_slot
    invalid_offering.location = hamilton_city  # Hamilton is not in instructor's availability

    # Add the invalid offering to the catalog
    offering_catalog._offerings[invalid_offering.offering_id] = invalid_offering

    # Check the constraint
    if invalid_offering.location.city_id not in instructor.available_cities:
        print(f"Constraint 3 violated: Offering {invalid_offering.offering_id} is in a city not in the instructor's availability.")
    else:
        print(f"Constraint 3 passed for offering {invalid_offering.offering_id}.")

    # ---------------------------
    # Constraint 4: Clients do not have overlapping bookings.
    # ---------------------------

    print("\n--- Testing Constraint 4: No Overlapping Bookings for Clients ---")

    # Create a client
    client = Client(
        client_id=generate_id(),
        email="client@example.com",
        password="password123",
        schedule_catalog=schedule_catalog,
        age=25
    )
    user_catalog.add_user(client)

    # Create two public offerings at the same time slot
    public_offering1 = PublicOffering(
        public_offering_id=generate_id(),
        offering=offering1,
        max_clients=5
    )
    public_offering1.reserved_timeslot_id_list = [time_slot]
    offering_catalog._public_offerings[public_offering1.public_offering_id] = public_offering1

    public_offering2 = PublicOffering(
        public_offering_id=generate_id(),
        offering=offering2,
        max_clients=5
    )
    public_offering2.reserved_timeslot_id_list = [time_slot]
    offering_catalog._public_offerings[public_offering2.public_offering_id] = public_offering2

    # Client books the first offering
    booking1 = Booking(
        booking_id=generate_id(),
        booked_by_client_id=client.client_id,
        public_offering_id=public_offering1.public_offering_id,
        booked_for_client_ids=[client.client_id]
    )
    booking_catalog.add_booking(booking1)
    client.bookings.append(booking1.booking_id)
    public_offering1.add_booking(booking1.booking_id)
    client.schedule.add_reserved_slots(public_offering1.reserved_timeslot_id_list)

    # Attempt to book the second offering at the same time slot
    booking2 = Booking(
        booking_id=generate_id(),
        booked_by_client_id=client.client_id,
        public_offering_id=public_offering2.public_offering_id,
        booked_for_client_ids=[client.client_id]
    )
    # Check for overlapping bookings
    client_timeslots = [ts for ts in client.schedule.get_reserved_slots()]
    offering_timeslots = public_offering2.reserved_timeslot_id_list
    overlap = False
    for ts in offering_timeslots:
        if ts in [slot.start_time for slot in client_timeslots]:
            overlap = True
            break
    if overlap:
        print(f"Constraint 4 violated: Client {client.client_id} has overlapping bookings.")
    else:
        # Proceed with booking
        booking_catalog.add_booking(booking2)
        client.bookings.append(booking2.booking_id)
        public_offering2.add_booking(booking2.booking_id)
        client.schedule.add_reserved_slots(public_offering2.reserved_timeslot_id_list)
        print(f"Constraint 4 passed: Client {client.client_id} booked without overlaps.")

if __name__ == "__main__":
    main()
