import Location as Loc
from Scheduling import TimeSlot, Schedule 
import datetime as dt


qc = Loc.Province(province_id=1, name="Quebec")
mtl = Loc.City(city_id=1, name="Montreal", province=qc)

ev_building = Loc.Branch(branch_id=1, name="EV Building", city=mtl)

ev_schedule = Schedule(schedule_id=1, branch=ev_building)

# Add time slots to the schedule
time_slot_1 = TimeSlot(time_slot_id=1, start_time=dt.datetime(2024, 9, 1, 12, 0), end_time=dt.datetime(2024, 9, 1, 13, 0))
time_slot_2 = TimeSlot(time_slot_id=2, start_time=dt.datetime(2024, 9, 1, 13, 0), end_time=dt.datetime(2024, 9, 1, 14, 0))

ev_schedule.add_time_slot(time_slot_1)
ev_schedule.add_time_slot(time_slot_2)

time_slot_1.reserve()

print("Available time slots:", ev_schedule.get_available_slots())
