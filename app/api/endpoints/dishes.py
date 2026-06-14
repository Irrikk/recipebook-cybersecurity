from typing import List, Optional
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.dish import Dish
from fastapi import Query

# Импортируем зависимости для БД
from app.db.session import get_db
from app.models.product import Product
from app.models.dish import Dish
from app.models.dish import DishProductLink
from app.models.enums import DishCategory
from app.schemas.dish import DishCreate, DishUpdate, DishOut

from app.services.dish_logic import process_dish_metadata
from app.services.calculator import calculate_full_dish_stats

router = APIRouter()

@router.post("/", response_model=DishOut, status_code=201)
def create_dish(dish_in: DishCreate, db: Session = Depends(get_db)):
    product_ids = [i.product_id for i in dish_in.ingredients]
    db_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    if len(db_products) != len(product_ids):
        raise HTTPException(status_code=404, detail="Некоторые продукты не найдены")

    cleaned_name, final_category = process_dish_metadata(dish_in.name, dish_in.category)
    if not final_category:
        raise HTTPException(status_code=400, detail="Категория не определена")

    stats = calculate_full_dish_stats(dish_in.ingredients, db_products)

    new_dish = Dish(
        name=cleaned_name,
        image_url=dish_in.image_url,
        category=final_category,
        portion_size=dish_in.portion_size,
        calories=dish_in.calories or stats["calories"],
        proteins=dish_in.proteins or stats["proteins"],
        fats=dish_in.fats or stats["fats"],
        carbs=dish_in.carbs or stats["carbs"],
        is_vegan=stats["is_vegan"],
        is_gluten_free=stats["is_gluten_free"],
        is_sugar_free=stats["is_sugar_free"]
    )
    
    db.add(new_dish)
    db.flush() 

    for ing in dish_in.ingredients:
        link = DishProductLink(dish_id=new_dish.id, product_id=ing.product_id, amount_g=ing.amount_g)
        db.add(link)

    db.commit()
    db.refresh(new_dish)
    return new_dish

@router.get("/", response_model=List[DishOut])
async def list_dishes(
    db: Session = Depends(get_db),
    category: Optional[DishCategory] = None,
    is_vegan: Optional[bool] = Query(None),
    is_gluten_free: Optional[bool] = Query(None),
    is_sugar_free: Optional[bool] = Query(None),
    search: Optional[str] = None,
    sort: str = Query("name")
):
    query = db.query(Dish).options(joinedload(Dish.ingredients))

    if search:
        query = query.filter(Dish.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Dish.category == category)
    if is_vegan:
        query = query.filter(Dish.is_vegan == True)
    if is_gluten_free:
        query = query.filter(Dish.is_gluten_free == True)
    if is_sugar_free:
        query = query.filter(Dish.is_sugar_free == True)

    sort_mapping = {
        "name": Dish.name,
        "calories": Dish.calories,
        "portion_size": Dish.portion_size
    }

    sort_column = sort_mapping.get(sort, Dish.name)
    
    query = query.order_by(sort_column)

    return query.all()

@router.get("/{dish_id}", response_model=DishOut)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(Dish)\
        .options(joinedload(Dish.ingredients))\
        .filter(Dish.id == dish_id)\
        .first()

    if not db_dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    return db_dish

@router.put("/{dish_id}", response_model=DishOut)
async def update_dish(dish_id: int, dish_in: DishUpdate, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    if dish_in.name:
        cleaned_name, new_category = process_dish_metadata(dish_in.name, dish_in.category)
        db_dish.name = cleaned_name
        if new_category:
            db_dish.category = new_category

    if dish_in.ingredients is not None:
        db.query(DishProductLink).filter(DishProductLink.dish_id == dish_id).delete()
        
        product_ids = [i.product_id for i in dish_in.ingredients]
        db_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        
        calc_cals = calc_prot = calc_fat = calc_carb = 0.0
        prod_map = {p.id: p for p in db_products}
        
        for ing in dish_in.ingredients:
            p = prod_map[ing.product_id]
            ratio = ing.amount_g / 100
            calc_cals += p.calories * ratio
            calc_prot += p.proteins * ratio
            calc_fat += p.fats * ratio
            calc_carb += p.carbs * ratio
            
            new_link = DishProductLink(dish_id=dish_id, product_id=ing.product_id, amount_g=ing.amount_g)
            db.add(new_link)

        db_dish.is_vegan = all(p.is_vegan for p in db_products)
        db_dish.is_gluten_free = all(p.is_gluten_free for p in db_products)
        db_dish.is_sugar_free = all(p.is_sugar_free for p in db_products)

        db_dish.calories = dish_in.calories or calc_cals
        db_dish.proteins = dish_in.proteins or calc_prot
        db_dish.fats = dish_in.fats or calc_fat
        db_dish.carbs = dish_in.carbs or calc_carb

    other_data = dish_in.dict(exclude_unset=True, exclude={"ingredients", "name", "category"})
    for field, value in other_data.items():
        setattr(db_dish, field, value)

    db.commit()
    db.refresh(db_dish)
    return db_dish

@router.delete("/{dish_id}", status_code=204)
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")
    
    db.delete(db_dish)
    db.commit()
    return None