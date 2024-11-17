from datetime import datetime, timedelta
from Models import Client, Instructor, Branch, Offering, Booking

class OCLTests:
    @staticmethod
    def unique_offering_per_location():
        """Ensure offerings are unique per location and time slot."""
        # Hardcoded example data
        branch1 = Branch(location_id="1", name="Branch 1", city="City A")
        branch2 = Branch(location_id="2", name="Branch 2", city="City B")
        offering1 = Offering(offering_id="1", location=branch1, start_time=datetime(2023, 12, 1, 10, 0), end_time=datetime(2023, 12, 1, 11, 0))
        offering2 = Offering(offering_id="2", location=branch1, start_time=datetime(2023, 12, 1, 10, 30), end_time=datetime(2023, 12, 1, 11, 30))
        offering3 = Offering(offering_id="3", location=branch2, start_time=datetime(2023, 12, 1, 10, 0), end_time=datetime(2023, 12, 1, 11, 0))
        
        offerings = [offering1, offering2, offering3]

        # OCL Test
        for i, o1 in enumerate(offerings):
            for o2 in offerings[i+1:]:
                if o1.location == o2.location and not (o1.end_time <= o2.start_time or o2.end_time <= o1.start_time):
                    print(f"Failed: Offering conflict at location {o1.location.name} and time slot {o1.start_time} - {o1.end_time}")
                    return False
        print("Passed: All offerings have unique locations per time slot.")
        return True

    @staticmethod
    def underage_must_have_adult_guardian():
        """Ensure underage clients have an adult guardian."""
        # Hardcoded example data
        adult_client = Client(user_id="1", name="Adult Client", age=25)
        underage_client_no_guardian = Client(user_id="2", name="Underage Client 1", age=16)
        underage_client_with_adult_guardian = Client(user_id="3", name="Underage Client 2", age=16, guardian_id=adult_client.user_id)
        adult_client.dependents = [underage_client_with_adult_guardian]

        clients = [adult_client, underage_client_no_guardian, underage_client_with_adult_guardian]

        # OCL Test
        for client in clients:
            if client.age < 18:
                guardian = client.guardian
                if not guardian or guardian.age < 18:
                    print(f"Failed: Underage client {client.name} (age {client.age}) does not have a valid adult guardian.")
                    return False
        print("Passed: All underage clients have an adult guardian.")
        return True

    @staticmethod
    def offering_city_in_instructor_availability():
        """Ensure the offering city is among the instructor's available cities."""
        # Hardcoded example data
        instructor = Instructor(user_id="1", name="Instructor A")
        branch1 = Branch(location_id="1", name="Branch 1", city="City A")
        branch2 = Branch(location_id="2", name="Branch 2", city="City B")
        instructor.availabilities = [branch1]  # Instructor available only in City A
        offering = Offering(offering_id="1", instructor=instructor, location=branch2)  # Offered in City B
        
        # OCL Test
        if not any(branch.city == offering.location.city for branch in instructor.availabilities):
            print(f"Failed: Offering city {offering.location.city} not in instructor {instructor.name}'s availability.")
            return False
        print("Passed: All offering cities are in instructor availability.")
        return True

    @staticmethod
    def no_overlapping_bookings():
        """Ensure clients do not have multiple bookings on the same day and time slot."""
        # Hardcoded example data
        client = Client(user_id="1", name="Client A")
        booking1 = Booking(booking_id="1", client=client, public_offering=Offering(start_time=datetime(2023, 12, 1, 10, 0), end_time=datetime(2023, 12, 1, 11, 0)))
        booking2 = Booking(booking_id="2", client=client, public_offering=Offering(start_time=datetime(2023, 12, 1, 10, 30), end_time=datetime(2023, 12, 1, 11, 30)))
        
        client.bookings = [booking1, booking2]

        # OCL Test
        for i, b1 in enumerate(client.bookings):
            for b2 in client.bookings[i+1:]:
                if not (b1.public_offering.end_time <= b2.public_offering.start_time or b2.public_offering.end_time <= b1.public_offering.start_time):
                    print(f"Failed: Client {client.name} has overlapping bookings at {b1.public_offering.start_time} - {b1.public_offering.end_time}")
                    return False
        print("Passed: No overlapping bookings for any client.")
        return True

    @staticmethod
    def run_ocl_test(test_number):
        """Run a specific OCL test based on test number."""
        if test_number == '1':
            print("--- Testing Unique Offering Per Location ---")
            return OCLTests.unique_offering_per_location()
        elif test_number == '2':
            print("--- Testing Underage Client Guardian ---")
            return OCLTests.underage_must_have_adult_guardian()
        elif test_number == '3':
            print("--- Testing Offering City in Instructor Availability ---")
            return OCLTests.offering_city_in_instructor_availability()
        elif test_number == '4':
            print("--- Testing No Overlapping Bookings ---")
            return OCLTests.no_overlapping_bookings()
        else:
            print("Invalid test number.")
            return False

    @staticmethod
    def ocl_test_menu():
        print("\n--- OCL Test Menu ---")
        print("1. Test Unique Offering Per Location")
        print("2. Test Underage Client Guardian")
        print("3. Test Offering City in Instructor Availability")
        print("4. Test No Overlapping Bookings")
        print("5. Exit OCL Tests")
        
        choice = input("Select an OCL test to run: ")
        if choice == '5':
            return
        OCLTests.run_ocl_test(choice)
        print()
