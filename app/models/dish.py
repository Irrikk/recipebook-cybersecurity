from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from .enums import DishCategory

class DishProductLink(Base):
    __tablename__ = 'dish_products'
    
    dish_id = Column(Integer, ForeignKey('dishes.id', ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    amount_g = Column(Float, nullable=False)

class Dish(Base):
    __tablename__ = 'dishes'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    category = Column(Enum(DishCategory), nullable=False)
    portion_size = Column(Float, nullable=False)
    
    calories = Column(Float, default=0.0)
    proteins = Column(Float, default=0.0)
    fats = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_sugar_free = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ingredients = relationship("DishProductLink", cascade="all, delete-orphan")