CREATE TABLE "provinces" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "cities" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar,
  "province_id" char(36)
);

CREATE TABLE "branches" (
  "location_id" char(36) PRIMARY KEY,
  "name" varchar,
  "city_id" char(36),
  "schedule_id" char(36)
);

CREATE TABLE "location_catalog" (
  "location_id" char(36),
  "entity_type" varchar,
  PRIMARY KEY ("location_id", "entity_type")
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

CREATE TABLE "instructor_city_availability" (
  "instructor_id" char(36),
  "city_id" char(36),
  PRIMARY KEY ("instructor_id", "city_id")
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

CREATE TABLE "user_catalog" (
  "user_id" char(36),
  "entity_type" varchar,
  PRIMARY KEY ("user_id", "entity_type")
);

CREATE TABLE "schedule_catalog" (
  "schedule_id" char(36) PRIMARY KEY,
  "owner_type" varchar,
  "owner_id" char(36)
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
  "capacity" integer
);

CREATE TABLE "public_offerings" (
  "offering_id" char(36),
  "instructor_id" char(36),
  "schedule_id" char(36),
  "lesson_type" varchar,
  "mode" varchar,
  "capacity" integer,
  PRIMARY KEY ("offering_id", "instructor_id")
);

CREATE TABLE "offering_catalog" (
  "offering_id" char(36),
  "entity_type" varchar,
  PRIMARY KEY ("offering_id", "entity_type")
);

CREATE TABLE "bookings" (
  "booked_by_client_id" char(36),
  "public_offering_id" char(36),
  "booked_for_client_id" char(36),
  PRIMARY KEY ("booked_by_client_id", "public_offering_id")
);

CREATE TABLE "booking_catalog" (
  "booking_by_client_id" char(36),
  "booking_offering_id" char(36),
  "entity_type" varchar,
  PRIMARY KEY ("booking_by_client_id", "booking_offering_id")
);

CREATE INDEX ON "schedule_catalog" ("owner_type", "owner_id");

COMMENT ON TABLE "instructor_city_availability" IS 'Associates instructors with cities they are available to teach in';

COMMENT ON TABLE "clients" IS 'guardian_id can be null for clients without guardians';

COMMENT ON TABLE "schedule_catalog" IS 'owner_type determines which table owner_id references:
- When owner_type = "USER", owner_id references user_catalog.user_id
- When owner_type = "BRANCH", owner_id references branches.location_id
';

COMMENT ON COLUMN "schedule_catalog"."owner_type" IS 'Can be either "USER" or "BRANCH"';

COMMENT ON TABLE "booking_catalog" IS 'References composite primary key from bookings table';

ALTER TABLE "cities" ADD FOREIGN KEY ("province_id") REFERENCES "provinces" ("location_id");

ALTER TABLE "branches" ADD FOREIGN KEY ("city_id") REFERENCES "cities" ("location_id");

ALTER TABLE "provinces" ADD FOREIGN KEY ("location_id") REFERENCES "location_catalog" ("location_id");

ALTER TABLE "cities" ADD FOREIGN KEY ("location_id") REFERENCES "location_catalog" ("location_id");

ALTER TABLE "branches" ADD FOREIGN KEY ("location_id") REFERENCES "location_catalog" ("location_id");

ALTER TABLE "administrators" ADD FOREIGN KEY ("user_id") REFERENCES "user_catalog" ("user_id");

ALTER TABLE "instructors" ADD FOREIGN KEY ("user_id") REFERENCES "user_catalog" ("user_id");

ALTER TABLE "clients" ADD FOREIGN KEY ("user_id") REFERENCES "user_catalog" ("user_id");

ALTER TABLE "clients" ADD FOREIGN KEY ("user_id") REFERENCES "clients" ("guardian_id");

ALTER TABLE "user_catalog" ADD FOREIGN KEY ("user_id", "entity_type") REFERENCES "schedule_catalog" ("owner_id", "owner_type");

ALTER TABLE "branches" ADD FOREIGN KEY ("location_id") REFERENCES "schedule_catalog" ("owner_id");

ALTER TABLE "schedule_catalog" ADD FOREIGN KEY ("schedule_id") REFERENCES "branches" ("schedule_id");

ALTER TABLE "schedule_catalog" ADD FOREIGN KEY ("schedule_id") REFERENCES "instructors" ("schedule_id");

ALTER TABLE "schedule_catalog" ADD FOREIGN KEY ("schedule_id") REFERENCES "clients" ("schedule_id");

ALTER TABLE "time_slots" ADD FOREIGN KEY ("schedule_id") REFERENCES "schedule_catalog" ("schedule_id");

ALTER TABLE "public_offerings" ADD FOREIGN KEY ("offering_id") REFERENCES "offerings" ("offering_id");

ALTER TABLE "public_offerings" ADD FOREIGN KEY ("instructor_id") REFERENCES "instructors" ("user_id");

ALTER TABLE "public_offerings" ADD FOREIGN KEY ("schedule_id") REFERENCES "schedule_catalog" ("schedule_id");

ALTER TABLE "time_slots" ADD FOREIGN KEY ("reserved_by_public_offering_id") REFERENCES "public_offerings" ("offering_id");

ALTER TABLE "offerings" ADD FOREIGN KEY ("offering_id") REFERENCES "offering_catalog" ("offering_id");

ALTER TABLE "public_offerings" ADD FOREIGN KEY ("offering_id") REFERENCES "offering_catalog" ("offering_id");

ALTER TABLE "instructor_city_availability" ADD FOREIGN KEY ("instructor_id") REFERENCES "instructors" ("user_id");

ALTER TABLE "instructor_city_availability" ADD FOREIGN KEY ("city_id") REFERENCES "cities" ("location_id");

ALTER TABLE "bookings" ADD FOREIGN KEY ("booked_by_client_id") REFERENCES "clients" ("user_id");

ALTER TABLE "bookings" ADD FOREIGN KEY ("public_offering_id") REFERENCES "public_offerings" ("offering_id");

ALTER TABLE "bookings" ADD FOREIGN KEY ("booked_for_client_id") REFERENCES "clients" ("user_id");

ALTER TABLE "bookings" ADD FOREIGN KEY ("booked_by_client_id", "public_offering_id") REFERENCES "booking_catalog" ("booking_by_client_id", "booking_offering_id");
