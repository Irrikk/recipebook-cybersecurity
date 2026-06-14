from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import datetime
from app.models.enums import DishCategory

class IngredientEntry(BaseModel):
    product_id: int
    amount_g: float = Field(..., gt=0, description="Вес продукта в граммах")

class DishBase(BaseModel):
    name: str = Field(..., min_length=2)
    image_url: Optional[str] = None
    portion_size: float = Field(..., gt=0)
    category: Optional[DishCategory] = None
    
    calories: float = Field(default=0.0, ge=0)
    proteins: float = Field(default=0.0, ge=0)
    fats: float = Field(default=0.0, ge=0)
    carbs: float = Field(default=0.0, ge=0)

class DishCreate(DishBase):
    ingredients: List[IngredientEntry] = Field(..., min_length=1)

    @model_validator(mode='after')
    def validate_bju_limit(self) -> "DishCreate":
        total_bju = (self.proteins or 0) + (self.fats or 0) + (self.carbs or 0)
        
        if self.portion_size > 0:
            bju_per_100 = (total_bju / self.portion_size) * 100
            if bju_per_100 > 100:
                raise ValueError(f"Сумма БЖУ на 100г ({bju_per_100:.1f}) не может быть больше 100г")
        return self

class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    image_url: Optional[str] = None
    category: Optional[DishCategory] = None
    portion_size: Optional[float] = Field(None, gt=0)
    calories: Optional[float] = Field(None, ge=0)
    proteins: Optional[float] = Field(None, ge=0)
    fats: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    ingredients: Optional[List[IngredientEntry]] = None

class DishOut(DishBase):
    id: int
    ingredients: List[IngredientEntry] = []
    is_vegan: bool
    is_gluten_free: bool
    is_sugar_free: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True