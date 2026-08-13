from sqlalchemy.orm import Session

from shared.config import settings
from shared.models import DimName, FactNameYear, NameReaction, Person


def get_name_detail(db: Session, name_id: int, sex: str):
    dim = db.query(DimName).filter(DimName.id == name_id).one_or_none()
    if dim is None:
        return None

    year_rows = (
        db.query(FactNameYear)
        .filter(FactNameYear.name_id == name_id, FactNameYear.sex == sex)
        .order_by(FactNameYear.country_code, FactNameYear.year)
        .all()
    )

    reaction_rows = (
        db.query(NameReaction.reaction, Person.key)
        .join(Person, Person.id == NameReaction.person_id)
        .filter(NameReaction.name_id == name_id, NameReaction.sex == sex)
        .all()
    )
    reactions = {settings.person_a_key: None, settings.person_b_key: None}
    for reaction, person_key in reaction_rows:
        reactions[person_key] = reaction

    return {
        "name_id": dim.id,
        "name": dim.name,
        "sex": sex,
        "timeseries": [
            {
                "country_code": r.country_code,
                "year": r.year,
                "count": r.count,
                "rank": r.rank,
            }
            for r in year_rows
        ],
        "reactions": reactions,
    }
