import re
from typing import Optional, Tuple
from app.models.enums import DishCategory

MACRO_MAP = {
    "!десерт": DishCategory.DESSERT,
    "!первое": DishCategory.FIRST,
    "!второе": DishCategory.SECOND,
    "!напиток": DishCategory.DRINK,
    "!салат": DishCategory.SALAD,
    "!суп": DishCategory.SOUP,
    "!перекус": DishCategory.SNACK,
}

def process_dish_metadata(name: str, form_category: Optional[DishCategory]) -> Tuple[str, DishCategory]:
    words = name.split()
    detected_category = None
    cleaned_name_parts = []

    for word in words:
        low_word = word.lower()
        if low_word in MACRO_MAP:
            if not detected_category:
                detected_category = MACRO_MAP[low_word]
            continue
        cleaned_name_parts.append(word)

    final_name = " ".join(cleaned_name_parts)
    final_category = form_category or detected_category
    
    return final_name, final_category