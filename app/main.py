from fastapi import FastAPI
from app.api.endpoints import products, dishes
from app.db.session import engine, Base
from fastapi.middleware.cors import CORSMiddleware

# Эта строка cоздает все таблицы в базе данных 
# на основе моделей, которые импортированы в проекте
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Book API")

# Определяем список разрешенных адресов

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Подключаем Middleware к приложению
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Разрешаем запросы с этих адресов
    allow_credentials=True,         # Разрешаем передачу куки и заголовков авторизации
    allow_methods=["*"],            # Разрешаем все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],            # Разрешаем любые заголовки
)

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(dishes.router, prefix="/api/v1/dishes", tags=["dishes"])

@app.get("/")
async def root():
    return {"message": "Welcome to Recipe Book API"}