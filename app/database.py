from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_sqlite_column_migrations():
    """Add any model columns missing from an existing SQLite file.

    Base.metadata.create_all only creates tables that don't exist yet, so a
    database created before a column was added to a model needs it patched
    in by hand. Safe to run on every startup: it's a no-op once the column
    exists.
    """
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(visitors)"))}
        new_columns = (
            "registered_date",
            "registered_time",
            "registered_by",
            "checkin_by",
            "checkout_by",
        )
        for column in new_columns:
            if column not in existing:
                conn.execute(text(f"ALTER TABLE visitors ADD COLUMN {column} TEXT"))
        conn.commit()
