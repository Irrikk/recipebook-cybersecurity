from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from sqlalchemy import asc, desc
from app.models.product import Product
from sqlalchemy.orm import Session
from app.models.dish import Dish, DishProductLink
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.models.enums import ProductCategory, CookingNeed
from app.db.session import get_db


router = APIRouter()

@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    
    product_data = product_in.dict()
    
    new_product = Product(**product_data)
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/", response_model=List[ProductOut])
async def list_products(
    db: Session = Depends(get_db),
   
    category: Optional[ProductCategory] = None,
    cooking_need: Optional[CookingNeed] = None,
    is_vegan: Optional[bool] = Query(None),
    is_gluten_free: Optional[bool] = Query(None),
    is_sugar_free: Optional[bool] = Query(None),
    search: Optional[str] = None,
    sort_by: str = Query("name", regex="^(name|calories|proteins|fats|carbs)$"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category:
        query = query.filter(Product.category == category)
    if cooking_need:
        query = query.filter(Product.cooking_need == cooking_need)

    if is_vegan:
        query = query.filter(Product.is_vegan == True)
    if is_gluten_free:
        query = query.filter(Product.is_gluten_free == True)
    if is_sugar_free:
        query = query.filter(Product.is_sugar_free == True)

    column = getattr(Product, sort_by)
    if order == "asc":
        query = query.order_by(asc(column))
    else:
        query = query.order_by(desc(column))

    return query.all()

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), debug_calc: Optional[str] = None):
    # Намеренная уязвимость для SAST
    if debug_calc:
        # Уязвимость 1: Использование небезопасного eval() 

        print(f"Debug calculation result: {eval(debug_calc)}")

    db_product = db.query(Product).filter(Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
        
    return db_product

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, product_in: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    update_data = product_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
   
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    related_dishes = (
        db.query(Dish)
        .join(DishProductLink)
        .filter(DishProductLink.product_id == product_id)
        .all()
    )

    if related_dishes:
        dish_names = [dish.name for dish in related_dishes]
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": "deletion_blocked",
                "message": "Удаление невозможно: продукт используется в составе блюд.",
                "used_in_dishes": dish_names
            }
        )

    db.delete(product)
    db.commit()
    
    return None