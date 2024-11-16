I'll help fix the formatting while preserving the ## headers. Here's the corrected markdown:

# OCL Constraints Documentation

## 1. Offerings are unique. Multiple offerings on the same day and time slot must be offered at a different location.

**Implementation Note:** This constraint works with the `OfferedInBranch` association class and the `Branch` entities from the diagram, as locations are represented through the Branch hierarchy. We interpret uniqueness only through timing here as per our reading of the requirements. In real life this is of course untrue (judo != swimming) but it seems like that's what the assignment is saying.

```ocl
context Offering
inv UniqueOfferingPerLocation:
    Offering.allInstances()->forAll(o1, o2 |
        o1 <> o2 implies (
            o1.location <> o2.location or
            o1.end_time <= o2.start_time or
            o2.end_time <= o1.start_time
        )
    )
```

## 2. Any client who is underage must necessarily be accompanied by an adult who acts as their guardian.

**Implementation Note:** The Client class has a self-referential relationship with guardian_id as FK and methods getDependents()/getGuardian(), which directly supports this constraint.

```ocl
context Client
inv UnderageMustHaveAdultGuardian:
    self.age < 18 implies (
        self.guardian->notEmpty() and
        self.guardian.age >= 18
    )
```

## 3. The city associated with an offering must be one of the cities that the instructor has indicated in their availabilities.

**Implementation Note:** This involves the InstructorBranchAvailability association class that links Instructors with Branches and the branch relationship with city in the location hierarchy. The instructor chooses cities and then the branches are filled automatically.

```ocl
context Offering
inv OfferingCityInInstructorAvailability:
    self.instructor.availabilities.branch.city->exists(c |
        c = self.location.city
    )
```

## 4. A client does not have multiple bookings on the same day and time slot.

**Implementation Note:** This is enforced through the Schedule and Timeslot class structure, where a Timeslot can only be associated with one PublicOffering at a time.

The enforcement involves:
1. Timeslots as weak entities tied to schedule
2. One-to-one relationship between Timeslot and PublicOffering
3. Booking validation against timeslot availability

```ocl
context Client
inv NoOverlappingBookings:
    self.bookings->forAll(b1, b2 |
        b1 <> b2 implies (
            b1.publicOffering.end_time <= b2.publicOffering.start_time or
            b2.publicOffering.end_time <= b1.publicOffering.start_time
        )
    )
```