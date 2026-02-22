from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base
import app.models  # registers all ORM models with Base metadata
from app.models.work_code import WorkCode
from app.routers import auth, reports, work_codes, projects

DEFAULT_WORK_CODES = [
    (1, "Jalkojen poraus"),
    (2, "Rungon asennus ja suoristus"),
    (3, "Villan asennus"),
    (4, "Kipsilevyjen asennus"),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Add new nullable columns to existing SQLite databases gracefully
    _new_columns_work_entries = [
        ("work_entries", "area", "VARCHAR"),
        ("work_entries", "objects", "VARCHAR"),
        ("work_entries", "description", "VARCHAR"),
        ("weekly_reports", "project_id", "INTEGER"),
    ]
    with engine.connect() as conn:
        for table, col, col_type in _new_columns_work_entries:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass  # Column already exists
    with Session(engine) as db:
        for code, desc in DEFAULT_WORK_CODES:
            exists = (
                db.query(WorkCode)
                .filter(WorkCode.code == code, WorkCode.user_id == None)
                .first()
            )
            if not exists:
                db.add(WorkCode(code=code, description=desc, user_id=None))
        db.commit()
    yield


app = FastAPI(title="DoneGo API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost",
        "http://frontend",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(work_codes.router)
app.include_router(projects.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
