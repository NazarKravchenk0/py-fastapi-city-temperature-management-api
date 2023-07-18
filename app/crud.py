from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Cities ----------
def create_city(db: Session, city_in: schemas.CityCreate) -> models.City:
    city = models.City(name=city_in.name, additional_info=city_in.additional_info)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


def get_city(db: Session, city_id: int) -> models.City | None:
    return db.get(models.City, city_id)


def get_city_by_name(db: Session, name: str) -> models.City | None:
    stmt = select(models.City).where(models.City.name == name)
    return db.execute(stmt).scalar_one_or_none()


def list_cities(db: Session) -> list[models.City]:
    stmt = select(models.City).order_by(models.City.id.asc())
    return db.execute(stmt).scalars().all()


def update_city(db: Session, city: models.City, city_in: schemas.CityUpdate) -> models.City:
    if city_in.name is not None:
        city.name = city_in.name
    if city_in.additional_info is not None:
        city.additional_info = city_in.additional_info
    db.commit()
    db.refresh(city)
    return city


def delete_city(db: Session, city: models.City) -> None:
    db.delete(city)
    db.commit()


# ---------- Temperatures ----------
def create_temperature(db: Session, city_id: int, temperature_value: float) -> models.Temperature:
    t = models.Temperature(city_id=city_id, temperature=temperature_value)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def list_temperatures(db: Session, city_id: int | None = None) -> list[models.Temperature]:
    stmt = select(models.Temperature).order_by(models.Temperature.date_time.desc())
    if city_id is not None:
        stmt = stmt.where(models.Temperature.city_id == city_id)
    return db.execute(stmt).scalars().all()
