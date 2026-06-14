from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from datetime import datetime
from app.models.enums import ProductCategory, CookingNeed

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, description="Название продукта")
    image_url: Optional[str] = None
    category: ProductCategory
    cooking_need: CookingNeed = CookingNeed.READY
    
    # КБЖУ на 100г
    calories: float = Field(0.0, ge=0)
    proteins: float = Field(0.0, ge=0)
    fats: float = Field(0.0, ge=0)
    carbs: float = Field(0.0, ge=0)
    
    # Флаги
    is_vegan: bool = False
    is_gluten_free: bool = True
    is_sugar_free: bool = True

class ProductCreate(ProductBase):
    @model_validator(mode='after')
    def validate_bju_sum(self):
        total = self.proteins + self.fats + self.carbs
        
        if total > 100:
            raise ValueError(f"Сумма БЖУ ({total}) не может быть больше 100г на 100г продукта!")
        return self

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    image_url: Optional[str] = None
    category: Optional[ProductCategory] = None
    cooking_need: Optional[CookingNeed] = None
    calories: Optional[float] = Field(None, ge=0)
    proteins: Optional[float] = Field(None, ge=0)
    fats: Optional[float] = Field(None, ge=0)
    carbs: Optional[float] = Field(None, ge=0)
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_sugar_free: Optional[bool] = None

    @model_validator(mode='after')
    def validate_bju_sum(self):
        if self.proteins is not None and self.fats is not None and self.carbs is not None:
            total = self.proteins + self.fats + self.carbs
            if total > 100:
                raise ValueError(f"Сумма БЖУ ({total}) не может превышать 100г")
        return self

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)