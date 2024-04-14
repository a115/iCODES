from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime

from icds.settings import settings


class DbRepo(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    path: str | None = None
    remote_url: str | None = None
    description: str | None = None


class RepoCommit(SQLModel, table=True):
    id: int = Field(primary_key=True)
    repo_id: int = Field(foreign_key="dbrepo.id")
    hash: str
    datetime: datetime
    author: str
    commit_message: str
    file_stats: str | None = None
    summary: str
    details: str | None = None


engine = create_engine(settings.DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
