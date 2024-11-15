from System import System, generate_id  # Import System and generate_id
from Users import Instructor
from Offerings import Offering
from datetime import datetime
from Models import Client, Administrator  # Import Administrator directly from Models

def initialize_location_catalog(location_catalog, schedule_catalog):
    # Predefine provinces and cities without user input
    provinces_cities = {
        'Quebec': ['Montreal', 'Quebec City', 'Laval'],
        'Ontario': ['Toronto', 'Ottawa', 'Hamilton']
    }

    for province_name, city_names in provinces_cities.items():
        province = location_catalog.create_province(province_name)
        cities = [location_catalog.create_city(province.location_id, name) for name in city_names]

        for city in cities:
            for branch_num in range(1, 5):  # Creating four branches per city
                branch_name = f"{city.name} Branch {branch_num}"
                location_catalog.create_branch(city.location_id, branch_name, schedule_catalog)

def setup_admin_user(user_catalog):
    """Set up an administrator account."""
    admin = Administrator(
        user_id=generate_id(),
        email='admin@example.com',
        hashed_password='adminpass',
        name='Admin User'
    )
    user_catalog.add_user(admin)

def create_underage_client(user_catalog):
    """Attempt to create an underage client without a guardian to test the constraint."""
    underage_client = Client(
        user_id=generate_id(),
        email='underage@example.com',
        hashed_password='hashedpass',
        name='Underage Client',
        age=16,
        guardian_id=None  # No guardian specified
    )
    user_catalog.add_user(underage_client)
    return underage_client

def main():
    # Initialize system and catalogs
    system = System()
    user_catalog = system.user_catalog
    offering_catalog = system.offering_catalog
    location_catalog = system.location_catalog
    schedule_catalog = system.schedule_catalog

    # Preload locations and branches without user input
    initialize_location_catalog(location_catalog, schedule_catalog)

    # Set up an administrator (predefined in this example)
    setup_admin_user(user_catalog)

    # Create an underage client without a guardian to test Constraint 2
    underage_client = create_underage_client(user_catalog)

    try:
        system.session.commit()
        print("Underage client added without a guardian (Constraint 2 violated).")
    except Exception as e:
        system.session.rollback()
        print("Constraint 2 enforced: Underage client cannot be added without a guardian.")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
