from typer import Typer, echo, Argument, Option
from pathlib import Path

from loguru import logger
from git import Repo

from icds.git_helpers import extract_commit_info
from icds.llm_interface import analyse_commit
from icds.models import (
    create_db_and_tables,
    engine,
    RepoCommit,
    Session,
)
from icds.data import get_or_create_db_repo, get_repo_name_by_id, search_commits
from icds.settings import settings

app = Typer()


@app.command()
def inspect_repo(
    repo_path: Path, branch_name: str = "", n_commits: int = 10, detailed: bool = False
):
    """
    Inspect a git repository at a given path and branch. If no branch is provided, the current branch is used.
    Logs changes from the latest n_commits on the branch. If n_commits is not provided, a default maximum of 10
    commits are inspected.
    """
    repo = Repo(repo_path)
    if not branch_name:
        # Get the default branch configured for the repo
        branch_name = repo.active_branch.name
    logger.debug(f"Inspecting repo: {repo_path} on branch: {branch_name}")

    for commit in repo.iter_commits(branch_name, max_count=n_commits, reverse=True):
        commit_info = extract_commit_info(commit)
        analysis, summary = analyse_commit(commit_info)
        if detailed:
            echo(analysis + "\n")
        echo(
            f"Summary of commit #{commit} by {commit.author} from {commit.authored_datetime}: \n"
        )
        echo("\t" + summary + "\n")


@app.command()
def build_index(repo_path: Path, branch_name: str = "", n_commits: int = 10):
    """
    Build an index of the repository at the given path. If no branch is provided, the current branch is used.
    """
    repo = Repo(repo_path)
    if not branch_name:
        # Get the default branch configured for the repo
        branch_name = repo.active_branch.name

    logger.debug(
        f"Building index for repo: {repo_path} on branch: {branch_name}. Using model: {settings.DEFAULT_MODEL}. "
    )

    with Session(engine) as db:
        db_repo = get_or_create_db_repo(db, repo, repo_path)
        for commit in repo.iter_commits(branch_name, max_count=n_commits, reverse=True):
            commit_info = extract_commit_info(commit)
            echo(
                f"Indexing commit {commit.hexsha} by {commit.author} from {commit.authored_datetime} ... \n"
            )
            analysis, summary = analyse_commit(commit_info)

            diff = commit.diff(commit.parents[0])
            file_stats = []
            for change in diff:
                file_stats.append(f"{change.change_type} {change.a_path}")

            commit = RepoCommit(
                repo_id=db_repo.id,
                hash=commit.hexsha,
                datetime=commit.authored_datetime,
                author=str(commit.author),
                commit_message=commit.message,
                summary=commit.summary,
                details=analysis,
                file_stats="\n".join(file_stats),
            )
            db.add(commit)
            db.commit()
            echo("\t" + summary + "\n")


@app.command()
def search(
    query: str = Argument(..., help="Search query string"),
    repo_name: str = Option("", help="Filter by repository name"),
    author: str = Option("", help="Filter by commit author"),
    file: str = Option("", help="Filter by file path"),
    start_date: str = Option("", help="Filter commits after this date (YYYY-MM-DD)"),
    end_date: str = Option("", help="Filter commits before this date (YYYY-MM-DD)"),
):
    """
    Search the indexed commits for the given query string. Optionally filter by repository name, commit author, file
    path, and date range.
    """
    with Session(engine) as db:
        commits = search_commits(
            db, query, repo_name, file, author, start_date, end_date
        )
        for commit in commits:
            repo_name = get_repo_name_by_id(db, commit.repo_id)
            echo(f"Repository: {repo_name}")
            echo(f"Commit: {commit.hash}")
            echo(f"Author: {commit.author}")
            echo(f"Date: {commit.datetime}")
            echo(f"Summary: {commit.summary}")
            echo(f"Details: {commit.details}")
            echo("\n")


if __name__ == "__main__":
    create_db_and_tables()
    app()
