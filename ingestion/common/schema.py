from dataclasses import dataclass

NATIONAL = "NATIONAL"


@dataclass(frozen=True)
class NormalizedNameRecord:
    name: str
    sex: str  # "M" | "F"
    year: int
    country_code: str
    source: str
    count: int | None = None
    rank: int | None = None
    region_code: str = NATIONAL
