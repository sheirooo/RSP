class House:
    def __init__(self, house_id=0, flat_number=0, area=0.0, floor=0, rooms=0, street="", building_type="", lifetime=0):
        self.__id = house_id
        self.__flat_number = flat_number
        self.__area = area
        self.__floor = floor
        self.__rooms = rooms
        self.__street = street
        self.__building_type = building_type
        self.__lifetime = lifetime

        self.__fields = ["id", "flat_number", "area", "floor", "rooms", "street", "building_type", "lifetime"]

    # универсальный setter
    def set(self, key, value):
        if key in self.__fields:
            setattr(self, f"_{self.__class__.__name__}__{key}", value)
        else:
            raise KeyError(f"Поля '{key}' нет в классе House")

    # универсальный getter
    def get(self, key):
        if key in self.__fields:
            return getattr(self, f"_{self.__class__.__name__}__{key}")
        else:
            raise KeyError(f"Поля '{key}' нет в классе House")

    def __str__(self):
        return ", ".join([f"{field}: {self.get(field)}" for field in self.__fields])

    def __hash__(self):
        return hash((self.__id, self.__flat_number))

    def __eq__(self, other):
        if not isinstance(other, House):
            return False
        return self.__id == other.__id and self.__flat_number == other.__flat_number


class HouseManager:
    def __init__(self):
        self.houses = []

    def add_house(self, house):
        self.houses.append(house)

    # (a) список квартир с заданным числом комнат
    def get_houses_by_rooms(self, rooms):
        return [h for h in self.houses if h.get("rooms") == rooms]

    # (b) список квартир с заданным числом комнат и этажом в диапазоне
    def get_houses_by_rooms_and_floor(self, rooms, floor_min, floor_max):
        return [h for h in self.houses if h.get("rooms") == rooms and floor_min <= h.get("floor") <= floor_max]

    # (c) список квартир с площадью больше заданной
    def get_houses_by_area(self, min_area):
        return [h for h in self.houses if h.get("area") > min_area]


if __name__ == "__main__":
    manager = HouseManager()

    h1 = House(1, 101, 45.0, 2, 2, "Ленина", "Кирпичный", 50)
    h2 = House(2, 202, 65.5, 5, 3, "Победы", "Панельный", 40)
    h3 = House(3, 303, 38.0, 1, 1, "Советская", "Монолит", 70)

    h1.set("area", 47.5)
    h2.set("street", "Гагарина")

    manager.add_house(h1)
    manager.add_house(h2)
    manager.add_house(h3)

    print("(a) Квартиры с 2 комнатами:")
    for h in manager.get_houses_by_rooms(2):
        print(h)

    print("\n(b) Квартиры с 3 комнатами на этажах 2-6:")
    for h in manager.get_houses_by_rooms_and_floor(3, 2, 6):
        print(h)

    print("\n(c) Квартиры с площадью больше 40 кв.м:")
    for h in manager.get_houses_by_area(40):
        print(h)