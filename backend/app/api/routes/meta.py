from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas import CountryMeta, PersonMeta
from shared.config import settings
from shared.db import get_session
from shared.models import Country, FactNameYear, Person

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/countries", response_model=list[CountryMeta])
def get_countries(db: Session = Depends(get_session)):
    rows = (
        db.query(
            FactNameYear.country_code,
            func.min(FactNameYear.year).label("min_year"),
            func.max(FactNameYear.year).label("max_year"),
        )
        .group_by(FactNameYear.country_code)
        .all()
    )
    display_names = {c.code: c.display_name for c in db.query(Country).all()}
    return [
        CountryMeta(
            country_code=r.country_code,
            display_name=display_names.get(r.country_code, r.country_code),
            min_year=r.min_year,
            max_year=r.max_year,
        )
        for r in rows
    ]


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
