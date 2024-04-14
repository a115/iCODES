from loguru import logger
from sqlmodel import Session, select

from icds.models import engine, DbRepo, RepoCommit


def get_repo_by_name(name: str):
    with Session(engine) as session:
        statement = select(DbRepo).where(DbRepo.name == name)
        repo = session.exec(statement).first()
        return repo


def get_or_create_db_repo(db, repo, repo_path):
    remote_url = repo.remotes.origin.url
    repo_name = remote_url.split("/")[-1].split(".")[0]
    db_repo = get_repo_by_name(repo_name)
    if not db_repo:
        logger.info(f"Creating a new repository record for repo '{repo_name}'")
        db_repo = DbRepo(
            name=repo_name,
            path=str(repo_path),
            remote_url=remote_url,
        )
        db.add(db_repo)
        db.commit()
    return db_repo


def get_repo_name_by_id(db, repo_id):
    return db.exec(select(DbRepo).where(DbRepo.id == repo_id)).first().name


def search_commits(db, query, repo_name, file, author, start_date, end_date):
    statement = select(RepoCommit)
    if repo_name:
        db_repo = get_repo_by_name(repo_name)
        if not db_repo:
            raise ValueError(f"Repository '{repo_name}' not found.")
        statement = statement.where(RepoCommit.repo_id == db_repo.id)
    if author:
        statement = statement.where(RepoCommit.author == author)
    if file:
        statement = statement.where(RepoCommit.file_stats.contains(file))
    if start_date:
        statement = statement.where(RepoCommit.datetime >= start_date)
    if end_date:
        statement = statement.where(RepoCommit.datetime <= end_date)
    statement = statement.where(
        (RepoCommit.details.contains(query)) | (RepoCommit.summary.contains(query))
    )
    commits = db.exec(statement).all()
    return commits
