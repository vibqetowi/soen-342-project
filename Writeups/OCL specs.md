# OCL Constraints Documentation

## 1. Offerings are unique. Multiple offerings on the same day and time slot must be offered at a different location.
**Implementation Note:** This constraint will need to work with the `OfferedInBranch` association class and the `Branch` entities from the diagram, as locations are represented through the Branch hierarchy.
```ocl
context Offering
inv UniqueOfferingPerLocation:
 Offering.allInstances()->forAll(o1, o2 |
 o1 <> o2 implies (o1.timeSlot <> o2.timeSlot or o1.location <> o2.location)
 )
```

## 2. Any client who is underage must necessarily be accompanied by an adult who acts as their guardian.
**Implementation Note:** The Client class in the diagram has a self-referential relationship with guardian_id as FK and methods getDependents()/getGuardian(), which directly supports this constraint.
```ocl
context Client
inv UnderageMustHaveGuardian:
 self.age < 18 implies self.guardian->notEmpty()
```

## 3. The city associated with an offering must be one of the cities that the instructor has indicated in their availabilities.
**Implementation Note:** This involves the InstructorBranchAvailability association class that links Instructors with Branches, and the Branch's relationship to City in the location hierarchy.
```ocl
context Offering
inv OfferingCityInInstructorAvailability:
 self.instructor.availableCities->includes(self.location.city)
```

## 4. A client does not have multiple bookings on the same day and time slot.
**Implementation Note:** This constraint involves the Booking association class between Client and PublicOffering, where bookings store both booked_by_client_id and booked_for_client_id.
```ocl
context Client
inv NoOverlappingBookings:
 self.publicOfferings->forAll(o1, o2 |
 o1 <> o2 implies o1.timeSlot <> o2.timeSlot
 )
```