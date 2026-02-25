from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    bookings = relationship("Booking", back_populates="user")
    is_admin = Column(Boolean, default=False)
class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True)
    capacity = Column(Integer)  # вместимость
    bookings = relationship("Booking", back_populates="table")
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    guests_count = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    user = relationship("User", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")
