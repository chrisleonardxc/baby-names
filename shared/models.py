from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base

NATIONAL = "NATIONAL"


class DimName(Base):
    __tablename__ = "dim_name"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    name_lower: Mapped[str] = mapped_column(nullable=False, unique=True)
    length: Mapped[int] = mapped_column(nullable=False)
    starting_letter: Mapped[str] = mapped_column(nullable=False)
    syllable_count: Mapped[int | None] = mapped_column(nullable=True)

    year_facts: Mapped[list["FactNameYear"]] = relationship(back_populates="name")
    agg_facts: Mapped[list["FactNameCountrySexAgg"]] = relationship(back_populates="name")
    reactions: Mapped[list["NameReaction"]] = relationship(back_populates="name")


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(nullable=False)
    notes: Mapped[str | None] = mapped_column(nullable=True)


class FactNameYear(Base):
    __tablename__ = "fact_name_year"
    __table_args__ = (
        UniqueConstraint(
            "name_id", "country_code", "region_code", "sex", "year", "source",
            name="uq_fact_name_year_scope",
        ),
        CheckConstraint("sex IN ('M', 'F')", name="ck_fact_name_year_sex"),
        Index("ix_fact_name_year_country_sex_year", "country_code", "sex", "year"),
        Index("ix_fact_name_year_country_sex_year_rank", "country_code", "sex", "year", "rank"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name_id: Mapped[int] = mapped_column(ForeignKey("dim_name.id"), nullable=False)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), nullable=False)
    region_code: Mapped[str] = mapped_column(nullable=False, default=NATIONAL)
    sex: Mapped[str] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    count: Mapped[int | None] = mapped_column(nullable=True)
    rank: Mapped[int | None] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(nullable=False)

    name: Mapped["DimName"] = relationship(back_populates="year_facts")


class FactNameCountrySexAgg(Base):
    __tablename__ = "fact_name_country_sex_agg"
    __table_args__ = (
        Index("ix_agg_country_sex_best_rank", "country_code", "sex", "best_rank"),
    )

    name_id: Mapped[int] = mapped_column(ForeignKey("dim_name.id"), primary_key=True)
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"), primary_key=True)
    sex: Mapped[str] = mapped_column(primary_key=True)

    best_rank: Mapped[int | None] = mapped_column(nullable=True)
    total_count: Mapped[int] = mapped_column(nullable=False, default=0)
    first_year: Mapped[int | None] = mapped_column(nullable=True)
    last_year: Mapped[int | None] = mapped_column(nullable=True)
    trend: Mapped[str | None] = mapped_column(nullable=True)
    trend_slope: Mapped[float | None] = mapped_column(nullable=True)

    name: Mapped["DimName"] = relationship(back_populates="agg_facts")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(nullable=False)

    reactions: Mapped[list["NameReaction"]] = relationship(back_populates="person")


class NameReaction(Base):
    __tablename__ = "name_reactions"
    __table_args__ = (
        UniqueConstraint("person_id", "name_id", "sex", name="uq_name_reactions_scope"),
        CheckConstraint("sex IN ('M', 'F')", name="ck_name_reactions_sex"),
        CheckConstraint("reaction IN ('favorite', 'veto')", name="ck_name_reactions_reaction"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    name_id: Mapped[int] = mapped_column(ForeignKey("dim_name.id"), nullable=False)
    sex: Mapped[str] = mapped_column(nullable=False)
    reaction: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    person: Mapped["Person"] = relationship(back_populates="reactions")
    name: Mapped["DimName"] = relationship(back_populates="reactions")
