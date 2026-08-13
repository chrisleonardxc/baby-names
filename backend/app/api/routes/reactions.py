from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas import ReactionOut, ReactionUpdate
from app.services.reactions import list_reactions, set_reaction
from shared.db import get_session

router = APIRouter(prefix="/api/reactions", tags=["reactions"])


@router.post("", response_model=ReactionOut)
def post_reaction(payload: ReactionUpdate, db: Session = Depends(get_session)):
    if payload.reaction is not None and payload.reaction not in ("favorite", "veto"):
        raise HTTPException(status_code=422, detail="reaction must be 'favorite', 'veto', or null")
    try:
        result = set_reaction(db, payload.person_key, payload.name_id, payload.sex, payload.reaction)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return ReactionOut(person_key=payload.person_key, name_id=payload.name_id, sex=payload.sex, reaction=result)


@router.get("", response_model=list[ReactionOut])
def get_reactions(person_key: str = Query(...), db: Session = Depends(get_session)):
    try:
        rows = list_reactions(db, person_key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return [
        ReactionOut(person_key=person_key, name_id=r.name_id, sex=r.sex, reaction=r.reaction) for r in rows
    ]
