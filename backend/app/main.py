import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, meta, names, reactions
from app.auth import require_auth
from shared.config import settings
from shared.db import SessionLocal, init_db
from shared.models import FactNameYear
from shared.seed import seed_countries, seed_people

logger = logging.getLogger("baby_names")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Baby Name Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(meta.router, dependencies=[Depends(require_auth)])
app.include_router(names.router, dependencies=[Depends(require_auth)])
app.include_router(reactions.router, dependencies=[Depends(require_auth)])


@app.on_event("startup")
def on_startup():
    init_db()
    session = SessionLocal()
    try:
        seed_countries(session)
        seed_people(session)
        has_data = session.query(FactNameYear.id).first() is not None
        if not has_data:
            logger.warning(
                "No name data loaded yet. Run `make seed` (or `make seed-country COUNTRY=us`) "
                "to load the vendored baby-name datasets."
            )
    finally:
        session.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
