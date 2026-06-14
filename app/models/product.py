from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean
from app.db.session import Base
from .enums import ProductCategory, CookingNeed

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    category = Column(Enum(ProductCategory), nullable=False)
    cooking_need = Column(Enum(CookingNeed), default=CookingNeed.READY)
    
    # КБЖУ на 100г продукта
    calories = Column(Float, default=0.0)
    proteins = Column(Float, default=0.0)
    fats = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    
    # Флаги
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=True)
    is_sugar_free = Column(Boolean, default=True)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)