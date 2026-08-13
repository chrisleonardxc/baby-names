from sqlalchemy.orm import Session

from shared.models import NameReaction, Person


def set_reaction(db: Session, person_key: str, name_id: int, sex: str, reaction: str | None):
    person = db.query(Person).filter(Person.key == person_key).one_or_none()
    if person is None:
        raise ValueError(f"unknown person_key: {person_key}")

    existing = (
        db.query(NameReaction)
        .filter(
            NameReaction.person_id == person.id,
            NameReaction.name_id == name_id,
            NameReaction.sex == sex,
        )
        .one_or_none()
    )

    if reaction is None:
        if existing is not None:
            db.delete(existing)
            db.commit()
        return None

    if existing is not None:
        existing.reaction = reaction
    else:
        existing = NameReaction(person_id=person.id, name_id=name_id, sex=sex, reaction=reaction)
        db.add(existing)
    db.commit()
    return reaction


def list_reactions(db: Session, person_key: str):
    person = db.query(Person).filter(Person.key == person_key).one_or_none()
    if person is None:
        raise ValueError(f"unknown person_key: {person_key}")
    rows = db.query(NameReaction).filter(NameReaction.person_id == person.id).all()
    return rows
