from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./recipe_book.db"

# engine — это фактическое соединение с базой
# check_same_thread=False нужен только для SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal — это класс, который будет создавать сессии базы данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base — класс, от которого мы наследуем модели (в файлах models/product.py и т.д.)
Base = declarative_base()

# Dependency (зависимость), которую мы используем в роутах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()