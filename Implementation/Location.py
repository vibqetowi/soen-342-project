from singleton_decorator import singleton
from sqlalchemy.orm import Session
from Database import SessionLocal
from utils import generate_id
from Models import Province, City, Branch

@singleton
class LocationCatalog:
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()

    def create_province(self, name):
        """Create a new province and add it to the catalog."""
        province_id = generate_id()
        province = Province(location_id=province_id, name=name)
        self.session.add(province)
        self.session.commit()
        return province

    def get_province(self, province_id):
        """Retrieve a province by its ID."""
        return self.session.query(Province).filter_by(location_id=province_id).first()

    def get_province_by_name(self, name):
        """Retrieve a province by its name."""
        return self.session.query(Province).filter_by(name=name).first()

    def create_city(self, province_id, name):
        """Create a new city and add it to the catalog."""
        province = self.get_province(province_id)
        if not province:
            raise ValueError("Province not found.")

        city_id = generate_id()
        city = City(location_id=city_id, name=name, parent_location_id=province_id)
        self.session.add(city)
        self.session.commit()
        return city

    def get_city(self, city_id):
        """Retrieve a city by its ID."""
        return self.session.query(City).filter_by(location_id=city_id).first()

    def get_city_by_name(self, name):
        """Retrieve a city by its name."""
        return self.session.query(City).filter_by(name=name).first()

    def create_branch(self, city_id, name, schedule_catalog):
        """Create a new branch and add it to the catalog."""
        city = self.get_city(city_id)
        if not city:
            raise ValueError("City not found.")

        branch_id = generate_id()
        branch = Branch(location_id=branch_id, name=name, parent_location_id=city_id)
        self.session.add(branch)
        self.session.commit() 

        schedule = schedule_catalog.create_schedule(branch_id, "branch")
        branch.schedule_id = schedule.schedule_id 

        self.session.commit() 
        return branch

    def get_branch(self, branch_id):
        """Retrieve a branch by its ID."""
        return self.session.query(Branch).filter_by(location_id=branch_id).first()

    def get_branch_by_name(self, name):
        """Retrieve a branch by its name."""
        return self.session.query(Branch).filter_by(name=name).first()
