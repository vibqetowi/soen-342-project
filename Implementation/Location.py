from Scheduling import ScheduleCatalog
from System import generate_id
from singleton_decorator import singleton

@singleton
class LocationCatalog:
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)  # Create a new instance if it doesn't exist
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Ensure __init__ is only called once
            self._initialized = True
            self._provinces = {}  # Internal storage for Province objects
            self._provinces_by_name = {}  # Hashtable for Province names
            self._cities = {}     # Internal storage for City objects
            self._cities_by_name = {}  # Hashtable for City names
            self._branches = {}   # Internal storage for Branch objects
            self._branches_by_name = {}  # Hashtable for Branch names

    def create_province(self, name):
        """Create a new province and add it to the catalog."""
        province_id = generate_id()
        province = _Province(province_id, name)
        self._provinces[province_id] = province
        self._provinces_by_name[name] = province  # Store by name
        return province

    def get_province(self, province_id):
        """Retrieve a province by its ID."""
        return self._provinces.get(province_id)

    def get_province_by_name(self, name):
        """Retrieve a province by its name."""
        return self._provinces_by_name.get(name)

    def create_city(self, province_id, name):
        """Create a new city and add it to the catalog."""
        province = self.get_province(province_id)
        if not province:
            raise ValueError("Province not found.")
        
        city = province.create_city(name)
        self._cities[city.city_id] = city
        self._cities_by_name[name] = city  # Store by name
        return city

    def get_city(self, city_id):
        """Retrieve a city by its ID."""
        return self._cities.get(city_id)

    def get_city_by_name(self, name):
        """Retrieve a city by its name."""
        return self._cities_by_name.get(name)

    def create_branch(self, city_id, name, schedule_catalog):
        """Create a new branch and add it to the catalog."""
        city = self.get_city(city_id)
        if not city:
            raise ValueError("City not found.")
        
        branch = city.create_branch(name, schedule_catalog)
        self._branches[branch.branch_id] = branch
        self._branches_by_name[name] = branch  # Store by name
        return branch

    def get_branch(self, branch_id):
        """Retrieve a branch by its ID."""
        return self._branches.get(branch_id)

    def get_branch_by_name(self, name):
        """Retrieve a branch by its name."""
        return self._branches_by_name.get(name)


class _Province:
    """Private class representing a Province."""
    def __init__(self, province_id, name):
        self.province_id = province_id
        self.name = name
        self._cities = {}  # Internal storage for City objects
        self._cities_by_name = {}  # Hashtable for City names

    def create_city(self, name):
        """Create a new city and add it to the province."""
        city_id = generate_id()
        city = _City(city_id, name, self)
        self._cities[city_id] = city
        self._cities_by_name[name] = city  # Store by name
        return city

    def get_city(self, city_id):
        """Retrieve a city by its ID."""
        return self._cities.get(city_id)

    def get_city_by_name(self, name):
        """Retrieve a city by its name."""
        return self._cities_by_name.get(name)


class _City:
    """Private class representing a City."""
    def __init__(self, city_id, name, province):
        self.city_id = city_id
        self.name = name
        self.province = province
        self._branches = {}  # Internal storage for Branch objects
        self._branches_by_name = {}  # Hashtable for Branch names

    def create_branch(self, name, schedule_catalog):
        """Create a new branch and add it to the city."""
        branch_id = generate_id()
        branch = _Branch(branch_id, name, self, schedule_catalog)
        self._branches[branch_id] = branch
        self._branches_by_name[name] = branch  # Store by name
        return branch

    def get_branch(self, branch_id):
        """Retrieve a branch by its ID."""
        return self._branches.get(branch_id)

    def get_branch_by_name(self, name):
        """Retrieve a branch by its name."""
        return self._branches_by_name.get(name)


class _Branch:
    """Private class representing a Branch."""
    def __init__(self, branch_id, name, city, schedule_catalog):
        self.branch_id = branch_id
        self.name = name
        self.city = city
        self.schedule = schedule_catalog.create_schedule(branch_id)
