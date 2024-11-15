from System import System, generate_id, Administrator  # Import System and generate_id
from Users import Instructor
from Offerings import Offering
from datetime import datetime
from Models import Client


def initialize_location_catalog(location_catalog, schedule_catalog):
    provinces_cities = {
        'Quebec': ['Montreal', 'Quebec City', 'Laval'],
        'Ontario': ['Toronto', 'Ottawa', 'Hamilton']
    }

    for province_name, city_names in provinces_cities.items():
        province = location_catalog.create_province(province_name)
        cities = [location_catalog.create_city(province.location_id, name) for name in city_names]

        for city in cities:
            for branch_num in range(1, 5):  # Four branches per city
                branch_name = f"{city.name} Branch {branch_num}"
                location_catalog.create_branch(city.location_id, branch_name, schedule_catalog)


def setup_admin_user():
    """Set up an administrator account."""
    admin_email = input("Enter admin email: ")
    admin_password = input("Enter admin password: ")
    admin_id = generate_id()
    return Administrator(admin_id=admin_id, email=admin_email, password=admin_password)


def create_instructor(user_catalog, schedule_catalog):
    """Create and add an instructor to the user catalog."""
    instructor_id = generate_id()
    instructor_name = input("Enter instructor name: ")
    instructor_phone = input("Enter instructor phone: ")
    instructor_specialization = input("Enter instructor specialization: ")
    instructor_email = input("Enter instructor email: ")
    instructor_password = input("Enter instructor password: ")

    instructor = Instructor(
        instructor_id=instructor_id,
        name=instructor_name,
        phone=instructor_phone,
        specialization=instructor_specialization,
        email=instructor_email,
        password=instructor_password,
        schedule_catalog=schedule_catalog
    )
    user_catalog.add_user(instructor)
    return instructor


def set_instructor_availability(instructor, cities):
    """Set instructor availability in specified cities."""
    for city in cities:
        if input(f"Set availability in {city.name}? (yes/no): ").lower() == "yes":
            instructor.set_availability(city.location_id)


def test_unique_offerings_constraint(offering_catalog, location_catalog, instructor_id):
    """Test if there are unique offerings per location."""
    print("\n--- Testing Constraint 1: Unique Offerings per Location ---")
    time_slot_str = input("Enter offering time slot (HH:MM, e.g., 10:00): ")
    time_slot = datetime.now().replace(hour=int(time_slot_str.split(":")[0]), minute=int(time_slot_str.split(":")[1]))

    offering1_location = location_catalog.get_city_by_name(input("Enter location name for Offering 1: "))
    offering2_location = location_catalog.get_city_by_name(input("Enter location name for Offering 2: "))

    offering1 = Offering(generate_id(), instructor_id, "Yoga", "Group", 10)
    offering1.time_slot = time_slot
    offering1.location = offering1_location

    offering2 = Offering(generate_id(), instructor_id, "Yoga", "Group", 10)
    offering2.time_slot = time_slot
    offering2.location = offering2_location

    offering_catalog._offerings[offering1.offering_id] = offering1
    offering_catalog._offerings[offering2.offering_id] = offering2

    # Check for uniqueness constraint
    offerings = list(offering_catalog._offerings.values())
    conflict_exists = any(
        o1.time_slot == o2.time_slot and o1.location == o2.location
        for i, o1 in enumerate(offerings) for j, o2 in enumerate(offerings) if i < j
    )
    if conflict_exists:
        print("Conflict detected: Multiple offerings at the same location and time slot.")
    else:
        print("Constraint 1 passed.")


def main():
    # Initialize system and catalogs
    system = System()
    user_catalog = system.user_catalog
    offering_catalog = system.offering_catalog
    location_catalog = system.location_catalog
    schedule_catalog = system.schedule_catalog

    # Preload locations and branches
    initialize_location_catalog(location_catalog, schedule_catalog)

    # Set up an administrator (hardcoded or minimal input)
    admin = Administrator(
        admin_id=generate_id(),
        email='admin@example.com',
        password='adminpass'
    )
    user_catalog.add_user(admin)
    system.session.commit()


    # Create an underage client without a guardian to test Constraint 2
    underage_client = Client(
        user_id=generate_id(),
        email='underage@example.com',
        hashed_password='hashedpass',
        name='Underage Client',
        age=16,
        guardian_id=None  # No guardian specified
    )
    user_catalog.add_user(underage_client)

    try:
        system.session.commit()
        print("Underage client added without a guardian (Constraint 2 violated).")
    except Exception as e:
        system.session.rollback()
        print("Constraint 2 enforced: Underage client cannot be added without a guardian.")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
