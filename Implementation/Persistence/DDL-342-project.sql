-- DROP EXISTING TABLES (if any) for a clean setup
DROP TABLE IF EXISTS time_slots, schedules, bookings, public_offerings, offerings, branches, cities, provinces, administrators, instructors, clients, audit_logs CASCADE;

-- Provinces table (no dependencies)
CREATE TABLE provinces (
    location_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Cities table (depends on Provinces)
CREATE TABLE cities (
    location_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    parent_location_id CHAR(36) REFERENCES provinces(location_id)
);

-- Administrators table (no dependencies)
CREATE TABLE administrators (
    user_id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Schedules table (no dependencies)
CREATE TABLE schedules (
    schedule_id CHAR(36) PRIMARY KEY,
    schedule_owner_id CHAR(36) NOT NULL,
    schedule_owner_type VARCHAR(50) NOT NULL
);

-- Instructors table (references Schedules)
CREATE TABLE instructors (
    user_id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    specialization VARCHAR(255),
    phone VARCHAR(20),
    schedule_id CHAR(36),
    FOREIGN KEY (schedule_id) REFERENCES schedules (schedule_id)
);

-- Clients table (references Schedules and self-referencing for guardian_id)
CREATE TABLE clients (
    user_id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT,
    guardian_id CHAR(36),
    schedule_id CHAR(36),
    FOREIGN KEY (guardian_id) REFERENCES clients (user_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules (schedule_id)
);

-- Branches table (depends on Cities and Schedules)
CREATE TABLE branches (
    location_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    schedule_id CHAR(36) REFERENCES schedules(schedule_id),
    parent_location_id CHAR(36) REFERENCES cities(location_id)
);

-- TimeSlots table (depends on Schedules)
CREATE TABLE time_slots (
    schedule_id CHAR(36) NOT NULL REFERENCES schedules(schedule_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_reserved BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (schedule_id, start_time)
);

-- Offerings table (depends on Instructors)
CREATE TABLE offerings (
    offering_id CHAR(36) PRIMARY KEY,
    instructor_id CHAR(36) REFERENCES instructors(user_id),
    lesson_type VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL,
    capacity INT NOT NULL
);

-- PublicOfferings table (depends on Offerings)
CREATE TABLE public_offerings (
    public_offering_id CHAR(36) PRIMARY KEY,
    offering_id CHAR(36) REFERENCES offerings(offering_id),
    max_clients INT NOT NULL
);

-- Bookings table (depends on Clients and PublicOfferings)
CREATE TABLE bookings (
    booking_id CHAR(36) PRIMARY KEY,
    booked_by_client_id CHAR(36) REFERENCES clients(user_id),
    public_offering_id CHAR(36) REFERENCES public_offerings(public_offering_id),
    booked_for_client_id CHAR(36) REFERENCES clients(user_id)
);
