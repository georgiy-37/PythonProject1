from pydantic import BaseModel, Field, field_validator
from datetime import datetime
class BookingCreate(BaseModel):
    table_id: int
    user_id: int
    start_time: datetime = Field(examples=["2026-02-13T15:00:00"])
    end_time: datetime = Field(examples=["2026-02-13T17:00:00"])
    guests_count: int = Field(ge=1, le=20)
    @field_validator("start_time")
    def start_time_future(cls, v):
        if v <= datetime.now():
            raise ValueError("Бронирование должно быть в будущем")
        return v
    @field_validator("end_time")
    def end_time_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("Время окончания должно быть позже начала")
        return v
class TableOut(BaseModel):
    id: int
    number: int
    capacity: int
    class Config: from_attributes = True
class BookingOut(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    table: TableOut
    guests_count: int
    class Config: from_attributes = True
class UserCreate(BaseModel):
    username: str
class UserOut(BaseModel):
    id: int
    username: str
    class Config: from_attributes = True
