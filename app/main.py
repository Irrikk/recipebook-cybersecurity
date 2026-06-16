from fastapi import FastAPI
from app.api.endpoints import products, dishes
from app.db.session import engine, Base
from fastapi.middleware.cors import CORSMiddleware
# Импортируем инструменты для создания кастомного Middleware и ответов
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Эта строка cоздает все таблицы в базе данных 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Book API")


# ТРИГГЕР ДЛЯ DAST: Подменяем заголовок сервера на уязвимый
class FakeVulnerableServerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        # Имитируем, что наш бэкенд работает на древнем и дырявом сервере Apache
        response.headers["Server"] = "Apache/2.0.52 (CentOS)"
        return response

# Регистрируем наш кастомный Middleware безопасности (точнее, "опасности" для теста)
app.add_middleware(FakeVulnerableServerMiddleware)


# Определяем список разрешенных адресов
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Подключаем CORS Middleware к приложению
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,         
    allow_methods=["*"],            
    allow_headers=["*"],            
)

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(dishes.router, prefix="/api/v1/dishes", tags=["dishes"])

@app.get("/")
async def root():
    return {"message": "Welcome to Recipe Book API"}


# ТРИГГЕРЫ ДЛЯ DAST: Оставляем "чувствительные" эндпоинты в корне

@app.get("/info.php")
def fake_php_info():
    # Имитируем оставленную разработчиком страницу конфигурации PHP
    return {"php_version": "5.3.3", "status": "exposed_debug_page", "note": "DAST Trigger"}

@app.get("/.env")
def fake_env_file():
    # Имитируем критическую утечку файла конфигурации окружения
    return {"DB_PASSWORD": "root_password_detected", "SECRET_KEY": "super_secret_ctf_key"}