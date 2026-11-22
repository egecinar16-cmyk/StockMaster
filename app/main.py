
import os

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine, SessionLocal

from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.user import User

from app.routers.products import router as products_router
from app.routers.customers import router as customers_router
from app.routers.orders import router as orders_router
from app.routers.reports import router as reports_router
from app.routers.auth import router as auth_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="StockMaster",
    description="Stok ve Sipariş Yönetim Sistemi",
    version="1.0.0"
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    same_site="lax",
    https_only=False
)


templates = Jinja2Templates(directory="app/templates")


# API bağlantıları
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(reports_router)
app.include_router(auth_router)


# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)


# Giriş yapan kullanıcıyı kontrol et
def get_logged_in_user(request: Request, db):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        request.session.clear()
        return None

    return user


# Ana yönetim paneli
@app.get("/")
def dashboard(request: Request):
    db = SessionLocal()

    try:
        user = get_logged_in_user(request, db)

        if not user:
            return RedirectResponse(
                url="/login",
                status_code=303
            )

        total_products = db.query(
            func.count(Product.id)
        ).filter(
            Product.user_id == user.id
        ).scalar() or 0

        total_customers = db.query(
            func.count(Customer.id)
        ).filter(
            Customer.user_id == user.id
        ).scalar() or 0

        total_orders = db.query(
            func.count(Order.id)
        ).filter(
            Order.user_id == user.id
        ).scalar() or 0

        total_sales = db.query(
            func.coalesce(func.sum(Order.total_amount), 0)
        ).filter(
            Order.user_id == user.id,
            Order.status != "Cancelled"
        ).scalar() or 0

        recent_orders = db.query(Order).filter(
            Order.user_id == user.id
        ).order_by(
            Order.id.desc()
        ).limit(5).all()

        low_stock_products = db.query(Product).filter(
            Product.user_id == user.id,
            Product.stock_quantity <= 5
        ).all()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "total_products": total_products,
                "total_customers": total_customers,
                "total_orders": total_orders,
                "total_sales": float(total_sales),
                "recent_orders": recent_orders,
                "low_stock_products": low_stock_products
            }
        )

    finally:
        db.close()


# Ürün yönetimi sayfası
@app.get("/product-management")
def product_management(request: Request):
    db = SessionLocal()

    try:
        user = get_logged_in_user(request, db)

        if not user:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "products.html",
            {"request": request, "user": user}
        )

    finally:
        db.close()


# Müşteri yönetimi sayfası
@app.get("/customer-management")
def customer_management(request: Request):
    db = SessionLocal()

    try:
        user = get_logged_in_user(request, db)

        if not user:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "customers.html",
            {"request": request, "user": user}
        )

    finally:
        db.close()


# Sipariş yönetimi sayfası
@app.get("/order-management")
def order_management(request: Request):
    db = SessionLocal()

    try:
        user = get_logged_in_user(request, db)

        if not user:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "orders.html",
            {"request": request, "user": user}
        )

    finally:
        db.close()


# Raporlar sayfası
@app.get("/reports-page")
def reports_page(request: Request):
    db = SessionLocal()

    try:
        user = get_logged_in_user(request, db)

        if not user:
            return RedirectResponse("/login", status_code=303)

        return templates.TemplateResponse(
            "reports.html",
            {"request": request, "user": user}
        )

    finally:
        db.close()


# Giriş ve kayıt sayfası
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth.html",
        {"request": request}
    )
