from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from Database import Base

class Administrator(Base):
    __tablename__ = 'administrators'
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)

class Instructor(Base):
    __tablename__ = 'instructors'
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    schedule_id = Column(String, ForeignKey('schedules.schedule_id'))

    schedule = relationship("Schedule", foreign_keys=[schedule_id])

class Client(Base):
    __tablename__ = 'clients'
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer)
    guardian_id = Column(String, ForeignKey('clients.user_id'))
    schedule_id = Column(String, ForeignKey('schedules.schedule_id'))

    schedule = relationship("Schedule", foreign_keys=[schedule_id])

class Booking(Base):
    __tablename__ = 'bookings'
    booking_id = Column(String, primary_key=True)
    booked_by_client_id = Column(String, ForeignKey('clients.user_id'))
    public_offering_id = Column(String, ForeignKey('public_offerings.public_offering_id'))
    booked_for_client_id = Column(String, ForeignKey('clients.user_id'))

    public_offering = relationship("PublicOffering", back_populates="bookings")
    booked_by_client = relationship("Client", foreign_keys=[booked_by_client_id])
    booked_for_client = relationship("Client", foreign_keys=[booked_for_client_id])

class Schedule(Base):
    __tablename__ = 'schedules'
    schedule_id = Column(String, primary_key=True)
    schedule_owner_id = Column(String, nullable=False)
    schedule_owner_type = Column(String, nullable=False)

    time_slots = relationship("TimeSlot", back_populates="schedule", cascade="all, delete-orphan")

class TimeSlot(Base):
    __tablename__ = 'time_slots'
    schedule_id = Column(String, ForeignKey('schedules.schedule_id'), primary_key=True)
    start_time = Column(DateTime, primary_key=True)
    end_time = Column(DateTime, nullable=False)
    is_reserved = Column(Boolean, default=False)

    schedule = relationship("Schedule", back_populates="time_slots")

class Offering(Base):
    __tablename__ = 'offerings'
    offering_id = Column(String, primary_key=True)
    instructor_id = Column(String, ForeignKey('instructors.user_id'))
    lesson_type = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)

    public_offerings = relationship("PublicOffering", back_populates="offering")

class PublicOffering(Base):
    __tablename__ = 'public_offerings'
    public_offering_id = Column(String, primary_key=True)
    offering_id = Column(String, ForeignKey('offerings.offering_id'))
    max_clients = Column(Integer, nullable=False)

    offering = relationship("Offering", back_populates="public_offerings")
    bookings = relationship("Booking", back_populates="public_offering")

class Province(Base):
    __tablename__ = 'provinces'
    location_id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    cities = relationship("City", back_populates="province", cascade="all, delete-orphan")

class City(Base):
    __tablename__ = 'cities'
    location_id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    parent_location_id = Column(String, ForeignKey('provinces.location_id'))

    province = relationship("Province", back_populates="cities")
    branches = relationship("Branch", back_populates="city", cascade="all, delete-orphan")

class Branch(Base):
    __tablename__ = 'branches'
    location_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    schedule_id = Column(String, ForeignKey('schedules.schedule_id'))
    parent_location_id = Column(String, ForeignKey('cities.location_id'))

    city = relationship("City", back_populates="branches")
    schedule = relationship("Schedule")
