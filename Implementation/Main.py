import sys
from System import System, generate_id
from Users import UserCatalog
from Location import LocationCatalog
from Scheduling import ScheduleCatalog
from Bookings import BookingCatalog
from Models import Client, Administrator, Instructor, Booking

def display_menu():
    print("\n--- Main Menu ---")
    print("1. Set up administrator user")
    print("2. Add new client")
    print("3. Add new instructor")
    print("4. Add a province and cities")
    print("5. Create a booking")
    print("6. Run OCL Test Mode")
    print("0. Exit")

def setup_admin_user(user_catalog):
    admin_email = input("Enter admin email: ")
    admin = Administrator(
        user_id=generate_id(),
        email=admin_email,
        hashed_password="adminpass",
        name="Admin"
    )
    user_catalog.add_user(admin)
    print("Admin user created successfully. Please change default credentials")

def add_client(user_catalog):
    print("\n--- Add New Client ---")
    email = input("Enter client email: ")
    password = input("Enter client password: ")
    name = input("Enter client name: ")
    age = int(input("Enter client age: "))

    client = Client(
        user_id=generate_id(),
        email=email,
        hashed_password=password,
        name=name,
        age=age
    )
    user_catalog.add_user(client)
    print("Client added successfully.")

def add_instructor(user_catalog):
    print("--- Add New Instructor ---")
    email = input("Enter instructor email: ")
    password = input("Enter instructor password: ")
    name = input("Enter instructor name: ")
    specialization = input("Enter instructor specialization: ")
    phone = input("Enter instructor phone: ")

    instructor = Instructor(
        user_id=generate_id(),
        email=email,
        hashed_password=password,  # You should hash this properly in production
        name=name,
        specialization=specialization,
        phone=phone,
    )
    user_catalog.add_user(instructor)
    print("Instructor added successfully!")

def add_province_and_cities(location_catalog):
    print("\n--- Add Province and Cities ---")
    province_name = input("Enter province name: ")
    city_names = input("Enter city names, separated by commas: ").split(',')

    province = location_catalog.create_province(province_name)
    for city_name in city_names:
        location_catalog.create_city(province.location_id, city_name.strip())
    print("Province and cities added successfully.")

def create_booking(booking_catalog, user_catalog):
    print("\n--- Create Booking ---")
    client_id = input("Enter client ID: ")
    offering_id = input("Enter offering ID: ")

    # Ensure client exists
    client = user_catalog.get_user_by_id(client_id)
    if not client:
        print("Client not found.")
        return
    
    booking = Booking(
        booking_id=generate_id(),
        booked_by_client_id=client_id,
        public_offering_id=offering_id
    )
    booking_catalog.add_booking(booking)
    print("Booking created successfully.")

def ocl_test_mode(user_catalog):
    print("\n--- OCL Test Mode ---")
    print("1. Test creating underage client")
    print("2. Test overbooking an offering")
    # Add other OCL tests here

    choice = input("Select a test case to run: ")
    
    if choice == '1':
        test_underage_client(user_catalog)
    elif choice == '2':
        test_overbooking()

def test_underage_client(user_catalog):
    print("\n--- Testing Underage Client ---")
    underage_client = Client(
        user_id=generate_id(),
        email="underage@example.com",
        hashed_password="pass123",
        name="2 User",
        age=12  # Example underage
    )
    try:
        user_catalog.add_user(underage_client)
        print("Underage client added successfully.")
    except ValueError as e:
        print("Failed to add underage client:", e)

def test_overbooking():
    # Placeholder for overbooking test
    print("\n--- Testing Overbooking ---")
    print("This feature is under development.")

def main():
    # Initialize system and catalogs
    system = System()
    user_catalog = system.user_catalog
    location_catalog = system.location_catalog
    schedule_catalog = system.schedule_catalog
    booking_catalog = system.booking_catalog

    while True:
        display_menu()
        choice = input("Select an option: ")

        if choice == '1':
            setup_admin_user(user_catalog)
        elif choice == '2':
            add_client(user_catalog)
        elif choice == '3':
            add_instructor(user_catalog)
        elif choice == '4':
            add_province_and_cities(location_catalog)
        elif choice == '5':
            create_booking(booking_catalog, user_catalog)
        elif choice == '6':
            ocl_test_mode(user_catalog)
        elif choice == '0':
            print("Exiting program.")
            sys.exit()
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
