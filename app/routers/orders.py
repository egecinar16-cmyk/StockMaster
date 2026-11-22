
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/orders", tags=["Orders"])


# Sadece kullanıcının kendi siparişlerini listele
@router.get("/")
def list_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Order).filter(
        Order.user_id == user.id
    ).all()


# Yeni sipariş oluştur
@router.post("/")
def create_order(
    customer_id: int = Form(...),
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Sipariş miktarı en az 1 olmalıdır."
        )

    # Müşterinin giriş yapan kullanıcıya ait olduğunu kontrol et
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.user_id == user.id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Müşteri bulunamadı."
        )

    # Ürünün giriş yapan kullanıcıya ait olduğunu kontrol et
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).with_for_update().first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı."
        )

    if product.stock_quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail="Yetersiz stok!"
        )

    try:
        unit_price = product.price
        total_amount = unit_price * quantity

        order = Order(
            user_id=user.id,
            customer_id=customer_id,
            total_amount=total_amount,
            status="Pending"
        )

        db.add(order)
        db.flush()

        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )

        product.stock_quantity -= quantity

        db.add(order_item)
        db.commit()
        db.refresh(order)

        return {
            "message": "Sipariş başarıyla oluşturuldu!",
            "order_id": order.id,
            "customer": customer.full_name,
            "product": product.name,
            "quantity": quantity,
            "total_amount": float(total_amount),
            "remaining_stock": product.stock_quantity
        }

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Sipariş oluşturulurken bir hata meydana geldi."
        )
