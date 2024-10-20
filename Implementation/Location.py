class Province:
    def __init__(self, province_id, name):
        self.province_id = province_id
        self.name = name
        self.cities = []

    def add_city(self, city):
        self.cities.append(city)


class City:
    def __init__(self, city_id, name, province):
        self.city_id = city_id
        self.name = name
        self.province = province
        self.branches = []
        province.add_city(self)

    def add_branch(self, branch):
        self.branches.append(branch)


class Branch:
    def __init__(self, branch_id, name, city):
        self.branch_id = branch_id
        self.name = name
        self.city = city
        self.schedules = []
        city.add_branch(self)

    def add_schedule(self, schedule):
        self.schedules.append(schedule)
