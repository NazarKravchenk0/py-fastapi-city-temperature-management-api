import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import crud, schemas
from ..services.weather import fetch_current_temperature, WeatherError

router = APIRouter(prefix="/temperatures", tags=["temperatures"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.TemperatureRead])
def list_temperatures(
    city_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    return crud.list_temperatures(db, city_id=city_id)


@router.post("/update", response_model=list[schemas.TemperatureUpdateResult])
async def update_temperatures(db: Session = Depends(get_db)):
    cities = crud.list_cities(db)
    if not cities:
        raise HTTPException(status_code=400, detail="No cities in database. Add cities first.")

    async def update_one(city):
        try:
            temp = await fetch_current_temperature(city.name)
            crud.create_temperature(db, city_id=city.id, temperature_value=temp)
            return schemas.TemperatureUpdateResult(
                city_id=city.id,
                city_name=city.name,
                ok=True,
                temperature=temp,
            )
        except (WeatherError, Exception) as e:
            return schemas.TemperatureUpdateResult(
                city_id=city.id,
                city_name=city.name,
                ok=False,
                error=str(e),
            )

    # Run all async fetches concurrently
    results = await asyncio.gather(*(update_one(c) for c in cities))
    return results
