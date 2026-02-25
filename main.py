from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from models import Booking, Table, User
from schemas import BookingCreate, BookingOut
from database import get_db
from sqlalchemy.orm import selectinload
from typing import Annotated
from fastapi.responses import RedirectResponse
from schemas import TableOut # Не забудь импорт
app = FastAPI(title="Restaurant Booking")
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
async def get_current_admin(token: str = Depends(oauth2_scheme)):
    # Пока мы не настроили JWT, просто создадим условие
    # В будущем здесь будет логика проверки токена
    is_admin = True # Временно для теста
    if token != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только для администраторов"
        )
    return is_admin
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
@app.post("/tables", response_model=TableOut)
async def create_table(number: int, capacity: int, db: AsyncSession = Depends(get_db), admin: bool = Depends(get_current_admin)):
    new_table = Table(number=number, capacity=capacity)
    db.add(new_table)
    await db.commit()
    await db.refresh(new_table)
    return new_table
@app.post("/bookings", response_model=BookingOut)
async def create_booking(data: BookingCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, существует ли стол и хватит ли у него мест
    table_query = select(Table).where(Table.id == data.table_id)
    table_res = await db.execute(table_query)
    table = table_res.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Стол не найден")
    if table.capacity < data.guests_count:
        raise HTTPException(
            status_code=400,
            detail=f"Этот стол вмещает только {table.capacity} чел., а вы указали {data.guests_count}"
        )
    # Главная фишка: проверяем пересечение интервалов времени
    query = select(Booking).where(
        and_(
            Booking.table_id == data.table_id,
            or_(
                and_(Booking.start_time <= data.start_time, Booking.end_time > data.start_time),
                and_(Booking.start_time < data.end_time, Booking.end_time >= data.end_time),
                and_(Booking.start_time >= data.start_time, Booking.end_time <= data.end_time)
            )
        )
    )
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Стол на это время уже занят")
    new_booking = Booking(**data.model_dump())
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking, ["table"])  # Подгружаем инфу о столе для ответа
    return new_booking
# 1. Удаление бронирования
@app.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db), admin: bool = Depends(get_current_admin)):
    query = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(query)
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    await db.delete(booking)
    await db.commit()
    return {"message": "Бронирование отменено"}
from datetime import datetime
# 1. Посмотреть все бронирования
@app.get("/bookings", response_model=list[BookingOut])
async def get_all_bookings(db: AsyncSession = Depends(get_db)):
    # selectinload подгрузит объект Table внутрь Booking
    query = select(Booking).options(selectinload(Booking.table))
    result = await db.execute(query)
    return result.scalars().all()
# 2. Найти свободные столы на указанный период
@app.get("/tables/free")
async def get_free_tables(start: datetime= Query(..., example="2026-02-13T15:00:00"), end: datetime = Query(..., example="2026-02-13T17:00:00"), db: AsyncSession = Depends(get_db)):
    # Ищем ID занятых столов
    occupied_query = select(Booking.table_id).where(
        or_(
            and_(Booking.start_time <= start, Booking.end_time > start),
            and_(Booking.start_time < end, Booking.end_time >= end)
        )
    )
    occupied_res = await db.execute(occupied_query)
    occupied_ids = occupied_res.scalars().all()
    # Берем столы, которых нет в списке занятых
    free_query = select(Table).where(Table.id.not_in(occupied_ids))
    result = await db.execute(free_query)
    return result.scalars().all()
@app.post("/users")
async def create_user(username: str, db: AsyncSession = Depends(get_db)):
    new_user = User(username=username)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
@app.put("/tables/{table_id}", response_model=TableOut)
async def update_table(
        table_id: int,
        capacity: Annotated[int, Query(ge=1, le=20)],  # Валидация: от 1 до 20 мест
        db: AsyncSession = Depends(get_db), admin: bool = Depends(get_current_admin)
):
    # 1. Ищем стол
    query = select(Table).where(Table.id == table_id)
    result = await db.execute(query)
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Стол не найден")
    # 2. Обновляем данные
    table.capacity = capacity
    # 3. Сохраняем
    await db.commit()
    await db.refresh(table)
    return table


