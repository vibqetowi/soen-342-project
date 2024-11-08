1) Offerings are unique. Multiple offerings on the same day and time slot must be offered at a different location.

```ocl
context Offering
inv UniqueOfferingPerLocation: 
    Offering.allInstances()->forAll(o1, o2 | 
        o1 <> o2 implies (o1.timeSlot <> o2.timeSlot or o1.location <> o2.location)
    )
```

2) Any client who is underage must necessarily be accompanied by an adult who acts as their guardian.

```ocl
context Client
inv UnderageMustHaveGuardian:
    self.age < 18 implies self.guardian->notEmpty()
```

3) The city associated with an offering must be one of the cities that the instructor has indicated in their availabilities.

```ocl
context Offering
inv OfferingCityInInstructorAvailability:
    self.instructor.availableCities->includes(self.location.city)
```

4) A client does not have multiple bookings on the same day and time slot.

```ocl
context Client
inv NoOverlappingBookings:
    self.publicOfferings->forAll(o1, o2 |
        o1 <> o2 implies o1.timeSlot <> o2.timeSlot
    )
```
