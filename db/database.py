import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Defaults to a local SQLite file so you can run everything with zero setup.
# Swap DATABASE_URL in your .env to a Postgres URL (e.g. from Supabase) when
# you're ready to deploy.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///opportunities.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
