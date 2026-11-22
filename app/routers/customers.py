
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/customers", tags=["Customers"])


# Sadece giriş yapan kullanıcının müşterilerini listele
@router.get("/")
def list_customers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Customer).filter(
        Customer.user_id == user.id
    ).all()


# Yeni müşteri ekle
@router.post("/")
def create_customer(
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    customer = Customer(
        user_id=user.id,
        full_name=full_name,
        email=email,
        phone=phone,
        address=address
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "message": "Müşteri başarıyla eklendi!",
        "customer": customer
    }


# Müşteri bilgilerini sadece sahibi güncelleyebilir
@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.user_id == user.id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Müşteri bulunamadı."
        )

    customer.full_name = full_name
    customer.email = email
    customer.phone = phone
    customer.address = address

    db.commit()
    db.refresh(customer)

    return {
        "message": "Müşteri güncellendi!",
        "customer": customer
    }


# Müşteriyi sadece sahibi silebilir
@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.user_id == user.id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Müşteri bulunamadı."
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Müşteri silindi!"
    }
