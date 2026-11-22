
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Kullanıcı kaydı
@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    username = username.strip()
    email = email.strip().lower()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Kullanıcı adı en az 3 karakter olmalıdır."
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Şifre en az 8 karakter olmalıdır."
        )

    existing_user = db.query(User).filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu kullanıcı adı veya e-posta zaten kayıtlı."
        )

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Bu kullanıcı adı veya e-posta zaten kayıtlı."
        )

    return {
        "message": "Kullanıcı başarıyla kaydedildi!",
        "username": user.username
    }


# Kullanıcı girişi ve oturum başlatma
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username.strip()
    ).first()

    if not user or not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya şifre hatalı."
        )

    request.session.clear()

    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return {
        "message": "Giriş başarılı!",
        "username": user.username
    }


# Kullanıcı çıkışı
@router.post("/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Başarıyla çıkış yapıldı."
    }
