from typing import List
from app.models.product import Product

def calculate_full_dish_stats(ingredients_with_weight: list, products_from_db: List[Product]):
   
    totals = {"calories": 0.0, "proteins": 0.0, "fats": 0.0, "carbs": 0.0}
    prod_map = {p.id: p for p in products_from_db}

    for ing in ingredients_with_weight:
        prod = prod_map.get(ing.product_id)
        if prod:
            ratio = ing.amount_g / 100.0
            totals["calories"] += prod.calories * ratio
            totals["proteins"] += prod.proteins * ratio
            totals["fats"] += prod.fats * ratio
            totals["carbs"] += prod.carbs * ratio
            
    flags = {
        "is_vegan": all(p.is_vegan for p in products_from_db),
        "is_gluten_free": all(p.is_gluten_free for p in products_from_db),
        "is_sugar_free": all(p.is_sugar_free for p in products_from_db),
    }
    
    return {**totals, **flags}