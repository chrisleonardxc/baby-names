from pydantic import BaseModel


class CountryMeta(BaseModel):
    country_code: str
    display_name: str
    min_year: int | None
    max_year: int | None


class PersonMeta(BaseModel):
    key: str
    display_name: str


class CountryStat(BaseModel):
    country_code: str
    best_rank: int | None
    total_count: int
    first_year: int | None
    last_year: int | None
    trend: str | None


class NameResult(BaseModel):
    name_id: int
    name: str
    sex: str
    starting_letter: str
    length: int
    syllable_count: int | None
    countries: list[CountryStat]
    reactions: dict[str, str | None]


class NamesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[NameResult]


class YearPoint(BaseModel):
    country_code: str
    year: int
    count: int | None
    rank: int | None


class NameDetail(BaseModel):
    name_id: int
    name: str
    sex: str
    timeseries: list[YearPoint]
    reactions: dict[str, str | None]


class ReactionUpdate(BaseModel):
    person_key: str
    name_id: int
    sex: str
    reaction: str | None = None


class ReactionOut(BaseModel):
    person_key: str
    name_id: int
    sex: str
    reaction: str | None
