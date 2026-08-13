from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas import NameDetail, NamesResponse
from app.services.name_detail import get_name_detail
from app.services.names_query import NameFilters, query_names
from app.services.reactions import get_favorited_name_sex
from app.services.shortlist import get_shortlist_name_sex
from shared.db import get_session

router = APIRouter(prefix="/api", tags=["names"])


def _parse_countries(countries: str | None) -> list[str] | None:
    if not countries:
        return None
    return [c.strip().upper() for c in countries.split(",") if c.strip()]


def _build_filters(
    sex: str,
    unisex_only: bool,
    countries: str | None,
    match_mode: str,
    year_min: int | None,
    year_max: int | None,
    rank_max: int | None,
    starting_letter: str | None,
    length_min: int | None,
    length_max: int | None,
    syllables_min: int | None,
    syllables_max: int | None,
    trend: str,
    viewer: str | None,
    exclude_vetoed: bool,
    sort_by: str,
    sort_dir: str,
    page: int,
    page_size: int,
) -> NameFilters:
    return NameFilters(
        sex=sex,
        unisex_only=unisex_only,
        countries=_parse_countries(countries),
        match_mode=match_mode,
        year_min=year_min,
        year_max=year_max,
        rank_max=rank_max,
        starting_letter=starting_letter,
        length_min=length_min,
        length_max=length_max,
        syllables_min=syllables_min,
        syllables_max=syllables_max,
        trend=trend,
        viewer=viewer,
        exclude_vetoed=exclude_vetoed,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@router.get("/names", response_model=NamesResponse)
def list_names(
    sex: str = Query("ALL", pattern="^(M|F|ALL)$"),
    unisex_only: bool = False,
    countries: str | None = None,
    match_mode: str = Query("any", pattern="^(any|all)$"),
    year_min: int | None = None,
    year_max: int | None = None,
    rank_max: int | None = None,
    starting_letter: str | None = Query(None, min_length=1, max_length=1),
    length_min: int | None = None,
    length_max: int | None = None,
    syllables_min: int | None = None,
    syllables_max: int | None = None,
    trend: str = Query("any", pattern="^(rising|falling|stable|any)$"),
    viewer: str | None = None,
    exclude_vetoed: bool = False,
    favorited_by: str | None = None,
    sort_by: str = Query("popularity", pattern="^(popularity|alpha|length)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_session),
):
    filters = _build_filters(
        sex, unisex_only, countries, match_mode, year_min, year_max, rank_max,
        starting_letter, length_min, length_max, syllables_min, syllables_max,
        trend, viewer, exclude_vetoed, sort_by, sort_dir, page, page_size,
    )
    if favorited_by:
        filters.restrict_name_sex = get_favorited_name_sex(db, favorited_by)
    total, results = query_names(db, filters)
    return NamesResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/shortlist", response_model=NamesResponse)
def get_shortlist(
    sex: str = Query("ALL", pattern="^(M|F|ALL)$"),
    unisex_only: bool = False,
    countries: str | None = None,
    match_mode: str = Query("any", pattern="^(any|all)$"),
    year_min: int | None = None,
    year_max: int | None = None,
    rank_max: int | None = None,
    starting_letter: str | None = Query(None, min_length=1, max_length=1),
    length_min: int | None = None,
    length_max: int | None = None,
    syllables_min: int | None = None,
    syllables_max: int | None = None,
    trend: str = Query("any", pattern="^(rising|falling|stable|any)$"),
    sort_by: str = Query("popularity", pattern="^(popularity|alpha|length)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_session),
):
    shortlist_set = get_shortlist_name_sex(db)
    filters = _build_filters(
        sex, unisex_only, countries, match_mode, year_min, year_max, rank_max,
        starting_letter, length_min, length_max, syllables_min, syllables_max,
        trend, None, False, sort_by, sort_dir, page, page_size,
    )
    filters.restrict_name_sex = shortlist_set
    total, results = query_names(db, filters)
    return NamesResponse(total=total, page=page, page_size=page_size, results=results)


@router.get("/names/{name_id}", response_model=NameDetail)
def name_detail(name_id: int, sex: str = Query(..., pattern="^(M|F)$"), db: Session = Depends(get_session)):
    detail = get_name_detail(db, name_id, sex)
    if detail is None:
        raise HTTPException(status_code=404, detail="name not found")
    return detail
