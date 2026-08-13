from sqlalchemy.orm import Session

from shared.models import NameReaction, Person


def get_shortlist_name_sex(db: Session) -> set[tuple[int, str]]:
    """(name_id, sex) pairs every seeded person favorited and none vetoed."""
    person_ids = {p.id for p in db.query(Person).all()}
    if not person_ids:
        return set()

    by_key: dict[tuple[int, str], dict[int, str]] = {}
    rows = db.query(
        NameReaction.name_id, NameReaction.sex, NameReaction.person_id, NameReaction.reaction
    ).all()
    for name_id, sex, person_id, reaction in rows:
        by_key.setdefault((name_id, sex), {})[person_id] = reaction

    result = set()
    for key, reactions_by_person in by_key.items():
        if any(r == "veto" for r in reactions_by_person.values()):
            continue
        favorited_by = {pid for pid, r in reactions_by_person.items() if r == "favorite"}
        if person_ids.issubset(favorited_by):
            result.add(key)
    return result
