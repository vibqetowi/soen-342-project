CREATE TABLE "permissions" (
  "permission_id" char(36) PRIMARY KEY,
  "name" varchar UNIQUE,
  "action_type" varchar
);

CREATE TABLE "user_permissions" (
  "permission_id" char(36),
  "table_name" varchar,
  "record_id" char(36),
  PRIMARY KEY ("permission_id", "table_name", "record_id")
);

CREATE TABLE "resource_permissions" (
  "permission_id" char(36),
  "table_name" varchar,
  "record_id" char(36),
  PRIMARY KEY ("permission_id", "table_name", "record_id")
);

CREATE TABLE "provinces" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "cities" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar,
  "parent_location_id" char(36)
);

CREATE TABLE "branches" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar,
  "schedule_id" char(36),
  "parent_location_id" char(36)
);

CREATE TABLE "administrators" (
  "user_id" char(36) PRIMARY KEY,
  "email" varchar UNIQUE,
  "hashed_password" varchar,
  "name" varchar
);

CREATE TABLE "instructors" (
  "user_id" char(36) PRIMARY KEY,
  "email" varchar UNIQUE,
  "hashed_password" varchar,
  "name" varchar,
  "phone" varchar,
  "specialization" varchar,
  "schedule_id" char(36)
);

CREATE TABLE "clients" (
  "user_id" char(36) PRIMARY KEY,
  "email" varchar UNIQUE,
  "hashed_password" varchar,
  "name" varchar,
  "schedule_id" char(36),
  "age" integer,
  "guardian_id" char(36)
);

CREATE TABLE "schedules" (
  "schedule_id" char(36) PRIMARY KEY,
  "table_name" varchar,
  "record_id" char(36)
);

CREATE TABLE "time_slots" (
  "schedule_id" char(36),
  "start_time" timestamp,
  "end_time" timestamp,
  "reserved_by_public_offering_id" char(36),
  "is_reserved" boolean,
  PRIMARY KEY ("schedule_id", "start_time")
);

CREATE TABLE "offerings" (
  "offering_id" char(36) PRIMARY KEY,
  "lesson_type" varchar,
  "mode" varchar,
  "capacity" integer,
  "duration" integer
);

CREATE TABLE "public_offerings" (
  "offering_id" char(36) PRIMARY KEY,
  "instructor_id" char(36),
  "schedule_id" char(36),
  "lesson_type" varchar,
  "mode" varchar,
  "capacity" integer,
  PRIMARY KEY ("offering_id", "instructor_id")
);

CREATE TABLE "instructor_branch_availability" (
  "instructor_id" char(36),
  "branch_id" char(36),
  PRIMARY KEY ("instructor_id", "branch_id")
);

CREATE TABLE "offered_in_branch" (
  "offering_id" char(36),
  "branch_id" char(36),
  PRIMARY KEY ("offering_id", "branch_id")
);

CREATE TABLE "bookings" (
  "booked_by_client_id" char(36),
  "public_offering_id" char(36),
  "booked_for_client_id" char(36),
  PRIMARY KEY ("booked_by_client_id", "public_offering_id")
);

CREATE TABLE "audit_logs" (
  "log_id" char(36) PRIMARY KEY,
  "timestamp" timestamp,
  "table_name" varchar,
  "actor_id" char(36),
  "action_type" varchar,
  "target_table" varchar,
  "record_id" char(36),
  "old_value" json,
  "new_value" json,
  "metadata" json
);

CREATE INDEX ON "schedules" ("record_id", "table_name");

ALTER TABLE "user_permissions"
ADD FOREIGN KEY ("permission_id")
REFERENCES "permissions" ("permission_id")
ON DELETE CASCADE;

ALTER TABLE "resource_permissions"
ADD FOREIGN KEY ("permission_id")
REFERENCES "permissions" ("permission_id")
ON DELETE CASCADE;

ALTER TABLE "cities"
ADD FOREIGN KEY ("parent_location_id")
REFERENCES "provinces" ("location_id")
ON DELETE CASCADE;

ALTER TABLE "branches"
ADD FOREIGN KEY ("parent_location_id")
REFERENCES "cities" ("location_id")
ON DELETE CASCADE;

ALTER TABLE "schedules"
ADD FOREIGN KEY ("schedule_id")
REFERENCES "branches" ("schedule_id")
ON DELETE CASCADE;

ALTER TABLE "schedules"
ADD FOREIGN KEY ("schedule_id")
REFERENCES "instructors" ("schedule_id")
ON DELETE CASCADE;

ALTER TABLE "schedules"
ADD FOREIGN KEY ("schedule_id")
REFERENCES "clients" ("schedule_id")
ON DELETE CASCADE;

ALTER TABLE "clients"
ADD FOREIGN KEY ("user_id")
REFERENCES "clients" ("guardian_id");

ALTER TABLE "time_slots"
ADD FOREIGN KEY ("schedule_id")
REFERENCES "schedules" ("schedule_id")
ON DELETE CASCADE;

ALTER TABLE "time_slots"
ADD FOREIGN KEY ("reserved_by_public_offering_id")
REFERENCES "public_offerings" ("offering_id")
ON DELETE CASCADE;

ALTER TABLE "offerings"
ADD FOREIGN KEY ("offering_id")
REFERENCES "public_offerings" ("offering_id")
ON DELETE CASCADE;

ALTER TABLE "public_offerings"
ADD FOREIGN KEY ("instructor_id")
REFERENCES "instructors" ("user_id")
ON DELETE CASCADE;

ALTER TABLE "schedules"
ADD FOREIGN KEY ("schedule_id")
REFERENCES "public_offerings" ("schedule_id")
ON DELETE CASCADE;

ALTER TABLE "instructor_branch_availability"
ADD FOREIGN KEY ("instructor_id")
REFERENCES "instructors" ("user_id")
ON DELETE CASCADE;

ALTER TABLE "instructor_branch_availability"
ADD FOREIGN KEY ("branch_id")
REFERENCES "branches" ("location_id")
ON DELETE CASCADE;

ALTER TABLE "offered_in_branch"
ADD FOREIGN KEY ("offering_id")
REFERENCES "offerings" ("offering_id")
ON DELETE CASCADE;

ALTER TABLE "offered_in_branch"
ADD FOREIGN KEY ("branch_id")
REFERENCES "branches" ("location_id")
ON DELETE CASCADE;

ALTER TABLE "bookings"
ADD FOREIGN KEY ("booked_by_client_id")
REFERENCES "clients" ("user_id")
ON DELETE CASCADE;

ALTER TABLE "bookings"
ADD FOREIGN KEY ("public_offering_id")
REFERENCES "public_offerings" ("offering_id")
ON DELETE CASCADE;

ALTER TABLE "bookings"
ADD FOREIGN KEY ("booked_for_client_id")
REFERENCES "clients" ("user_id")
ON DELETE CASCADE;