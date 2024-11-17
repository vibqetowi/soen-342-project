### System Contract for Creating an Offering

**Use Case**: Create Offering

**Actors**: Admin

**Preconditions**:
- The Admin is authenticated in the System.
- The offering ID does not already exist in the Offerings collection.

**Postconditions**:
- An offering with the specified attributes is created and added to the Offerings collection.
- The system confirms the creation of the offering to the Admin.

**Interaction Flow**:
1. Admin requests to create an offering with parameters (offering_id, lesson_type, mode).
2. System creates an instance of O:Offering using the provided parameters.
3. O:Offering confirms its creation to the System.
4. System adds O to the Offerings collection.
5. Offerings confirms to the System that the addition is successful.
6. System confirms the successful creation of the offering to the Admin.

---

### System Contract: User Deletion

**Contract Name:** User Deletion

**Preconditions:**
- The Admin is authenticated in the System.
- The user (Client or Instructor) with the specified ID exists in the respective collection.

**Input:**
- user_id : Integer (could refer to either Client or Instructor)

**Process:**
1. Determine the type of user (Client or Instructor) based on user_id.
2. Locate the user in the respective collection using user_id.
3. Request confirmation of deletion from the collection.
4. Collection deletes the instance.
5. The collection confirms deletion to the System.
6. System confirms the successful deletion to the Admin.

**Postconditions:**
- The specified user (Client or Instructor) is deleted from the respective collection.
- Confirmation of deletion is returned to the Admin.

**Output:**
- Confirm successful deletion to Admin.

---

### System Contract: Client Registration

**Contract Name:** Client Registration

**Preconditions:**
- User must provide an email, password, and age.

**Input:**
- email : String
- password : String
- age : Integer
- additional_args : Any additional required parameters

**Process:**
1. System hashes the provided password.
2. System generates a unique client ID.
3. If age < 18:
   - System requests guardian email from User.
   - UserCatalog searches for guardian using provided email.
   - If guardian found:
     - System verifies guardian's age is >= 18.
     - If guardian is minor, return error "Guardian must be 18+".
   - If guardian not found:
     - System sends invitation to guardian email.
4. UserCatalog creates new Client instance with generated ID and provided parameters.
5. New Client instance is added to Clients collection.
6. System confirms successful registration to User.

**Postconditions:**
- New client is added to Clients collection.
- If client is minor, they are either:
  - Associated with an existing guardian who is at least 18.
  - Pending guardian registration via invitation.
- User receives registration confirmation.

**Output:**
- Confirmation of registration to User.
- Error message if guardian age verification fails.

---

### System Contract: User Login

**Contract Name:** User Login

**Preconditions:**
- User must provide valid email and password.

**Input:**
- email : String
- password : String

**Process:**
1. System forwards login request to UserCatalog.
2. UserCatalog searches for user with provided email.
3. If user found:
   - System retrieves stored hashed password from user instance.
   - System hashes provided password.
   - System compares stored and provided hashed passwords.
   - If passwords match:
     - System confirms successful login.
   - If passwords don't match:
     - System returns error message.
4. If user not found:
   - System returns error message.

**Postconditions:**
- User is authenticated if credentials match.

**Output:**
- Confirmation of successful login to User.
- Error message if authentication fails.

---

### System Contract: Client Make Booking

**Contract Name:** Client Make Booking

**Preconditions:**
- User must provide a search query.
- User must be authenticated.

**Input:**
- search_query : String
- client_id : Integer

**Process:**
1. System verifies client's age:
   - If age < 18:
     - Return error "Minors cannot make bookings".
2. System prompts for booking type (self or child).
3. If booking for child:
   - System retrieves list of associated children.
   - User selects child from list.
   - System sets booking client ID to selected child.
4. System searches for available offerings matching query.
5. If offerings found:
   - System presents offerings to user.
   - User selects specific offering.
   - System checks offering capacity.
   - If capacity > 0:
     - System validates time slots against client's schedule.
     - If validation succeeds:
       - System generates booking ID.
       - System creates booking record.
       - System reserves time slots.
       - System confirms booking to user.
     - If validation fails:
       - System returns schedule conflict error.
   - If capacity <= 0:
     - System returns "offering full" error.
6. If no offerings found:
   - System returns "no offerings found" error.

**Postconditions:**
- New booking is created if all validations pass.
- Time slots are reserved in client's schedule.
- Offering capacity is updated.
- Client receives confirmation or appropriate error message.

**Output:**
- Booking confirmation or specific error message.

---

### System Contract: Client Cancel Booking

**Contract Name:** Client Cancel Booking

**Preconditions:**
- User must be authenticated.
- User must have existing bookings.

**Input:**
- client_id : Integer
- booking_id : Integer

**Process:**
1. System retrieves all bookings for client.
2. System displays bookings to user.
3. For each selected booking:
   - System retrieves booking details.
   - System identifies booked-for user.
   - System notifies booked-for user of cancellation.
   - System updates client's schedule.
   - System deletes booking record.
   - System confirms cancellation to user.

**Postconditions:**
- Selected booking(s) are removed from system.
- Client's schedule is updated.
- Affected users are notified.
- Offering capacity is adjusted.

**Output:**
- Confirmation of cancellation for each processed booking.

---

### System Contract: Reserve Time Slots

**Contract Name:** Reserve Time Slots

**Preconditions:**
- List of time slot IDs has been pre-validated.
- Schedule owner (User/Branch) exists.
- Public offering exists.

**Input:**
- time_slot_ids : List<TimeSlotId>
- public_offering_id : Integer
- schedule_owner_id : Integer

**Process:**
1. System retrieves schedule for the given owner ID from ScheduleCatalog.
2. For each time slot ID in the provided list:
   - System retrieves time slot from schedule.
   - System reserves the slot for the specified public offering.
   - System awaits confirmation of reservation.
3. System confirms all reservations completed successfully.

**Postconditions:**
- All specified time slots are reserved for the public offering.
- The schedule is updated with the new reservations.

**Output:**
- Confirmation of successful reservation.

---

### System Contract: Validate Time Slots

**Contract Name:** Validate Time Slots

**Preconditions:**
- Valid start and end times are provided.
- Schedule exists in the system.

**Input:**
- start_time : DateTime
- end_time : DateTime
- schedule_id : Integer

**Process:**
1. System calculates required time slots based on time range.
2. System retrieves schedule from ScheduleCatalog.
3. For each required time slot:
   - System retrieves time slot from schedule.
   - System checks slot availability.
   - If any slot is unavailable:
     - System returns error and terminates validation.
4. If all slots are available:
   - System returns list of valid time slot IDs.
5. Otherwise:
   - System returns error.

**Postconditions:**
- No changes to system state.
- List of valid time slot IDs or error message is prepared.

**Output:**
- List of valid time slot IDs if all slots are available.
- Error message if any slot is unavailable.

---

### System Contract: Generate ID

**Contract Name:** Generate ID

**Preconditions:**
- None, or valid arguments for composite key generation.

**Input:**
- args : Optional list of values for composite key generation

**Process:**
1. If no args provided:
   - System generates UUID v4.
   - System returns generated UUID.
2. If args provided:
   - System formats each argument:
     - Converts to string.
     - Removes special characters.
     - Converts to lowercase.
   - System combines formatted arguments with underscores.
   - System returns composite key.

**Postconditions:**
- New unique identifier is generated.

**Output:**
- UUID string if no args provided.
- Composite key string if args provided.

---

### System Contract: Create Location

**Contract Name:** Create Location

**Preconditions:**
- Admin is authenticated.
- Parent location exists if parent_location_id is provided.

**Input:**
- parent_location_id : Integer (optional)
- args : Additional location parameters (name, address, etc.)

**Process:**
1. System validates admin access.
2. System generates unique location ID.
3. System creates location instance with provided parameters.
4. LocationCatalog validates location hierarchy.
5. System adds location to Locations collection.
6. System confirms creation to admin.

**Postconditions:**
- New location is added to system.
- Location hierarchy remains valid.

**Output:**
- Confirmation of location creation.

---

### System Contract: Create Offering

**Contract Name:** Create Offering

**Preconditions:**
- Admin is authenticated.
- All specified branches exist.
- Valid time slots provided.

**Input:**
- branch_ids : List<Integer>
- start_time : DateTime
- end_time : DateTime
- args : Additional offering parameters

**Process:**
1. System validates admin access.
2. System generates unique offering ID.
3. For each branch:
   - System retrieves branch offerings.
   - System validates time slots for conflicts.
4. If conflicts detected:
   - System returns error message.
5. If no conflicts:
   - System creates new offering instance.
   - System adds offering to Offerings collection.
   - For each branch:
     - System associates offering with branch.
   - System confirms creation.

**Postconditions:**
- New offering is created if no conflicts.
- Offering is associated with specified branches.
- No time slot conflicts exist.

**Output:**
- Confirmation of offering creation or error message.

---

### System Contract: Edit User

**Contract Name:** Edit User

**Preconditions:**
- Admin is authenticated.
- User exists in system.

**Input:**
- user_id : Integer
- args : Updated user parameters

**Process:**
1. System validates admin access.
2. System retrieves user from UserCatalog.
3. System updates user profile with provided parameters.
4. System confirms update.

**Postconditions:**
- User profile is updated with new parameters.

**Output:**
- Confirmation of profile update.

---

### System Contract: Delete User

**Contract Name:** Delete User

**Preconditions:**
- Admin is authenticated.
- User exists in system.

**Input:**
- user_id : Integer

**Process:**
1. System validates admin access.
2. System retrieves user from UserCatalog.
3. System deletes user instance.
4. System confirms deletion.

**Postconditions:**
- User is removed from system.

**Output:**
- Confirmation of user deletion.

---

### System Contract: Edit Booking

**Contract Name:** Edit Booking

**Preconditions:**
- Admin is authenticated.
- Booking exists in system.

**Input:**
- booking_id : Integer
- args : Updated booking parameters

**Process:**
1. System validates admin access.
2. System retrieves booking from BookingCatalog.
3. System updates booking record with provided parameters.
4. System confirms update.

**Postconditions:**
- Booking record is updated with new parameters.

**Output:**
- Confirmation of booking update.

---

### System Contract: Delete Booking

**Contract Name:** Delete Booking

**Preconditions:**
- Admin is authenticated.
- Booking exists in system.

**Input:**
- booking_id : Integer

**Process:**
1. System validates admin access.
2. System retrieves booking from BookingCatalog.
3. System deletes booking instance.
4. System confirms deletion.

**Postconditions:**
- Booking is removed from system.

**Output:**
- Confirmation of booking deletion.

---

### System Contract: Edit Offering

**Contract Name:** Edit Offering

**Preconditions:**
- Admin is authenticated.
- Offering exists in system.

**Input:**
- offering_id : Integer
- args : Updated offering parameters

**Process:**
1. System validates admin access.
2. System retrieves offering from OfferingCatalog.
3. System updates offering record with provided parameters.
4. System confirms update.

**Postconditions:**
- Offering record is updated with new parameters.

**Output:**
- Confirmation of offering update.

---

### System Contract: Delete Base Offering

**Contract Name:** Delete Base Offering

**Preconditions:**
- Admin is authenticated.
- Base offering exists in system.

**Input:**
- offering_id : Integer

**Process:**
1. System validates admin access.
2. System retrieves offering from OfferingCatalog.
3. System deletes offering instance.
4. System confirms deletion.

**Postconditions:**
- Base offering is removed from system.

**Output:**
- Confirmation of offering deletion.

---

### System Contract: Delete Public Offering

**Contract Name:** Delete Public Offering

**Preconditions:**
- Admin is authenticated.
- Public offering exists in system.

**Input:**
- public_offering_id : Integer

**Process:**
1. System validates admin access.
2. System retrieves public offering from OfferingCatalog.
3. System retrieves all bookings associated with offering.
4. System deletes all associated bookings.
5. System deletes public offering instance.
6. System confirms deletion.

**Postconditions:**
- All associated bookings are removed.
- Public offering is removed from system.

**Output:**
- Confirmation of public offering and associated bookings deletion.