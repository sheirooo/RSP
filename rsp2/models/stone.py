class Stone:
    def __init__(self, name: str, weight: float, price: float, transparency: float):
        self._name = name
        self._weight = weight            # в каратах
        self._price = price              # цена за карат
        self._transparency = transparency  # 0–100 %

    @property
    def name(self):
        return self._name

    @property
    def weight(self):
        return self._weight

    @property
    def price(self):
        return self._price

    @property
    def transparency(self):
        return self._transparency

    def total_cost(self) -> float:
        return self._weight * self._price

    def __str__(self):
        return (f"{self._name} (вес: {self._weight} карат, "
                f"цена/карат: {self._price}, прозрачность: {self._transparency}%, "
                f"стоимость: {self.total_cost()})")
