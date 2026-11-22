
from typing import Optional
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/reports", tags=["Reports"])


# Günlük satış raporu
@router.get("/daily")
def daily_report(
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    selected_date = report_date or date.today()

    start = datetime.combine(selected_date, time.min)
    end = start + timedelta(days=1)

    result = db.query(
        func.count(Order.id),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.user_id == user.id,
        Order.created_at >= start,
        Order.created_at < end,
        Order.status != "Cancelled"
    ).first()

    return {
        "date": selected_date.isoformat(),
        "order_count": result[0],
        "total_sales": float(result[1])
    }


# Aylık satış raporu
@router.get("/monthly")
def monthly_report(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    today = date.today()

    selected_year = year if year is not None else today.year
    selected_month = month if month is not None else today.month

    if selected_month < 1 or selected_month > 12:
        raise HTTPException(
            status_code=400,
            detail="Ay değeri 1 ile 12 arasında olmalıdır."
        )

    if selected_year < 1 or selected_year > 9999:
        raise HTTPException(
            status_code=400,
            detail="Geçersiz yıl."
        )

    start = datetime(selected_year, selected_month, 1)

    if selected_month == 12:
        if selected_year == 9999:
            raise HTTPException(
                status_code=400,
                detail="Geçersiz tarih aralığı."
            )

        end = datetime(selected_year + 1, 1, 1)
    else:
        end = datetime(selected_year, selected_month + 1, 1)

    result = db.query(
        func.count(Order.id),
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.user_id == user.id,
        Order.created_at >= start,
        Order.created_at < end,
        Order.status != "Cancelled"
    ).first()

    return {
        "year": selected_year,
        "month": selected_month,
        "order_count": result[0],
        "total_sales": float(result[1])
    }
