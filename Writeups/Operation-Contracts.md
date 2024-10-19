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

**Process:**

1. Hash the password.
2. If age < 18:
   - Request guardian_id from User.
   - User provides guardian_id.
   - Find guardian in Clients using guardian_id.
   - Create new client with client_id, email, hashed_password, age, and guardian.
   - Add the new client to Clients.
3. If age >= 18:
   - Create new client with client_id, email, hashed_password, and age.
   - Add the new client to Clients.

**Postconditions:**

- New client is added to Clients.
- Clients under 18 are all associated with a guardian client that is at least 18.
- User is confirmed as registered.

**Output:**

- Confirm registration to User.

---

### System Contract: User Login

**Contract Name:** User Login

**Preconditions:**

- User must provide valid email and password.

**Input:**

- email : String
- password : String

**Process:**

1. Find the user in the Clients or Instructors collection using the provided email.
2. Retrieve stored_hashed_password from the found user instance.
3. Hash the provided password.
4. Check if stored_hashed_password matches hashed_password.
5. If matched, confirm login to User; otherwise, return error "invalid credentials."

**Postconditions:**

- User is authenticated if credentials match.

**Output:**

- If login is successful, confirm login to User.
- If login fails, return error "invalid credentials" to User.

---

### System Contract: Client Make Booking

**Contract Name:** Client Make Booking

**Preconditions:**

- User must provide a search_query.

**Input:**

- search_query : String

**Process:**

1. Find suitable Public Offering using search_query.
2. Retrieve capacity from PO:PublicOffering.
3. If capacity > 0:
   - Get available timeslots from PO:PublicOffering.
   - Find client in Clients.
   - Retrieve schedule from C:Client.
   - Get timeslots from C.Schedule:Schedule.
   - Check for overlap between PO.TimeSlots and C.Schedule.Timeslots.
   - If there is no overlap:
     - Add the Public Offering to the client's schedule.
     - Adjust capacity of the Public Offering.
   - Confirm booking to User.
4. If capacity <= 0:
   - Return error "all offerings full" to User.
5. If no suitable offering found:
   - Return error "no offering found" to User.

**Postconditions:**

- Public Offering is added to the client's schedule if booking is successful.
- There is no overlap in the client's schedule.
- Capacity of the Public Offering is decreased.

**Output:**

- Confirm booking to User, or error message as appropriate.

---

### System Contract: Client Cancel Booking

**Contract Name:** Client Cancel Booking

**Preconditions:**

- User must provide an offering_id from their schedule.

**Input:**

- offering_id : Integer

**Process:**

1. Find client in Clients.
2. Retrieve schedule from C:Client.
3. Find Public Offering in C.Schedule:Schedule using offering_id.
4. Remove Public Offering from the client's schedule.
5. Adjust capacity of the Public Offering.

**Postconditions:**

- Public Offering is removed from the client's schedule.
- Capacity of the Public Offering is increased.

**Output:**

- Confirm cancellation to User.
