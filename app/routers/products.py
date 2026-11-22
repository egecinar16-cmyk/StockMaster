
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/products", tags=["Products"])


# Ürünleri sadece giriş yapan kullanıcı için listele
@router.get("/")
def list_products(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    products = db.query(Product).filter(
        Product.user_id == user.id
    ).all()

    return products


# Yeni ürün ekle
@router.post("/")
def create_product(
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if price < 0 or stock_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Fiyat ve stok miktarı negatif olamaz."
        )

    product = Product(
        user_id=user.id,
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "message": "Ürün başarıyla eklendi!",
        "product": product
    }


# Ürün bilgilerini sadece sahibi güncelleyebilir
@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı."
        )

    if price < 0 or stock_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Fiyat ve stok negatif olamaz."
        )

    product.name = name
    product.description = description
    product.price = price
    product.stock_quantity = stock_quantity

    db.commit()
    db.refresh(product)

    return {
        "message": "Ürün güncellendi!",
        "product": product
    }


# Ürünü sadece sahibi silebilir
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı."
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Ürün başarıyla silindi!"
    }


# Sadece kullanıcının kritik stoktaki ürünlerini listele
@router.get("/low-stock")
def low_stock_products(
    threshold: int = 5,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if threshold < 0:
        raise HTTPException(
            status_code=400,
            detail="Stok sınırı negatif olamaz."
        )

    products = db.query(Product).filter(
        Product.user_id == user.id,
        Product.stock_quantity <= threshold
    ).all()

    return {
        "message": "Kritik stok kontrolü tamamlandı.",
        "threshold": threshold,
        "count": len(products),
        "products": products
    }
