from sqlalchemy.orm import Session

from shared.config import settings
from shared.models import Country, Person

COUNTRY_DISPLAY_NAMES = {
    "US": "United States",
    "GB": "United Kingdom",
    "FR": "France",
    "AU": "Australia",
    "CA": "Canada",
    "IE": "Ireland",
}


def seed_countries(session: Session) -> None:
    existing = {c.code for c in session.query(Country.code).all()}
    for code, display_name in COUNTRY_DISPLAY_NAMES.items():
        if code not in existing:
            session.add(Country(code=code, display_name=display_name))
    session.commit()


def seed_people(session: Session) -> None:
    wanted = [
        (settings.person_a_key, settings.person_a_name),
        (settings.person_b_key, settings.person_b_name),
    ]
    existing = {p.key: p for p in session.query(Person).all()}
    for key, display_name in wanted:
        if key in existing:
            if existing[key].display_name != display_name:
                existing[key].display_name = display_name
        else:
            session.add(Person(key=key, display_name=display_name))
    session.commit()
