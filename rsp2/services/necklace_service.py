class NecklaceService:
    def __init__(self):
        self._stones = []

    def add_stone(self, stone):
        self._stones.append(stone)

    def calculate_total_weight(self):
        return sum(stone.weight for stone in self._stones)

    def calculate_total_cost(self):
        return sum(stone.total_cost() for stone in self._stones)

    def sort_by_price(self):
        return sorted(self._stones, key=lambda s: s.total_cost())

    def find_by_transparency(self, min_t: float, max_t: float):
        return [
            s for s in self._stones
            if min_t <= s.transparency <= max_t
        ]

    @property
    def stones(self):
        return list(self._stones)
