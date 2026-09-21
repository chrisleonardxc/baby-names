from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas import CountryMeta, PersonMeta
from shared.config import settings
from shared.db import get_session
from shared.models import Country, FactNameYear, Person

router = APIRouter(prefix="/api/meta", tags=["meta"])


def _year_bound(db: Session, country_code: str, latest: bool) -> int | None:
    # One MIN/MAX per (country, sex) is a single seek on the (country_code, sex,
    # year) index; a GROUP BY across countries would scan every yearly row.
    agg = func.max if latest else func.min
    values = [
        db.query(agg(FactNameYear.year))
        .filter(FactNameYear.country_code == country_code, FactNameYear.sex == sex)
        .scalar()
        for sex in ("M", "F")
    ]
    values = [v for v in values if v is not None]
    if not values:
        return None
    return max(values) if latest else min(values)


@router.get("/countries", response_model=list[CountryMeta])
def get_countries(db: Session = Depends(get_session)):
    result = []
    for country in db.query(Country).order_by(Country.code).all():
        min_year = _year_bound(db, country.code, latest=False)
        if min_year is None:
            continue  # seeded country with no data loaded yet
        result.append(
            CountryMeta(
                country_code=country.code,
                display_name=country.display_name,
                min_year=min_year,
                max_year=_year_bound(db, country.code, latest=True),
            )
        )
    return result


@router.get("/people", response_model=list[PersonMeta])
def get_people(db: Session = Depends(get_session)):
    people = db.query(Person).order_by(Person.id).all()
    if people:
        return [PersonMeta(key=p.key, display_name=p.display_name) for p in people]
    # Fall back to configured defaults if the DB hasn't been seeded yet.
    return [
        PersonMeta(key=settings.person_a_key, display_name=settings.person_a_name),
        PersonMeta(key=settings.person_b_key, display_name=settings.person_b_name),
    ]
