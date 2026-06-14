from enum import Enum

class ProductCategory(str, Enum):
    FROZEN = "Замороженный"
    MEAT = "Мясной"
    VEGETABLES = "Овощи"
    GREENS = "Зелень"
    SPICES = "Специи"
    GRAINS = "Крупы"
    CANNED = "Консервы"
    LIQUID = "Жидкость"
    SWEETS = "Сладости"

class CookingNeed(str, Enum):
    READY = "Готовый к употреблению"
    SEMI_FINISHED = "Полуфабрикат"
    REQUIRES_COOKING = "Требует приготовления"

class DishCategory(str, Enum):
    DESSERT = "Десерт"
    FIRST = "Первое"
    SECOND = "Второе"
    DRINK = "Напиток"
    SALAD = "Салат"
    SOUP = "Суп"
    SNACK = "Перекус"