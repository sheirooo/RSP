from models.precious_stone import PreciousStone
from models.semiprecious_stone import SemiPreciousStone
from services.necklace_service import NecklaceService


def main():
    service = NecklaceService()

    service.add_stone(PreciousStone("Алмаз", 1.2, 5000, 98))
    service.add_stone(PreciousStone("Рубин", 2.1, 3200, 75))
    service.add_stone(SemiPreciousStone("Аметист", 3.5, 800, 65))
    service.add_stone(SemiPreciousStone("Сапфир", 5.0, 500, 40))

    while True:
        print("\n=== МЕНЮ ===")
        print("1. Показать все камни")
        print("2. Общая стоимость ожерелья")
        print("3. Общий вес")
        print("4. Сортировка по стоимости")
        print("5. Поиск по прозрачности")
        print("0. Выход")

        choice = input("Выберите пункт: ")

        match choice:
            case "1":
                for s in service.stones:
                    print(s)

            case "2":
                print("Общая стоимость:", service.calculate_total_cost())

            case "3":
                print("Общий вес:", service.calculate_total_weight(), "карат")

            case "4":
                print("Отсортированные камни:")
                for s in service.sort_by_price():
                    print(s)

            case "5":
                min_t = float(input("Минимальная прозрачность: "))
                max_t = float(input("Максимальная прозрачность: "))
                found = service.find_by_transparency(min_t, max_t)
                print("\nНайдено:")
                for s in found:
                    print(s)

            case "0":
                print("Выход...")
                return

            case _:
                print("Ошибка выбора!")


if __name__ == "__main__":
    main()
