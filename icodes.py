from typer import Typer, echo
from pathlib import Path
from difflib import unified_diff

from loguru import logger
from git import Repo

from icds.llm_interface import analyse_commit
from icds.models import (
    create_db_and_tables,
    engine,
    DbRepo,
    RepoCommit,
    Session,
    get_repo_by_name,
)
from icds.settings import settings

app = Typer()


def extract_commit_info(commit) -> str:
    output = "RepoCommit hash: {commit}\n"
    output += "RepoCommit date: {commit.authored_datetime}\n"
    output += "Author: {commit.author}\n"
    output += "Summary: {commit.summary}\n"
    if str(commit.message).strip() != str(commit.summary).strip():
        output += "Message: {commit.message}\n"

    output += "Changes:\n\n"

    # Get the diff of the commit with its parent
    diff = commit.diff(commit.parents[0])
    for change in diff:
        output += f"{change.change_type} {change.a_path}\n"
        if change.a_path.endswith(
            "poetry.lock"
        ):  # TODO: Extract this into a more robust sanitisation function
            continue
        # logger.info(f"New blob: \n{change.a_blob.data_stream.read().decode('utf-8')}")
        # logger.info(f"Old blob: \n{change.b_blob.data_stream.read().decode('utf-8')}")
        if change.b_blob and change.a_blob:
            for line in unified_diff(
                change.b_blob.data_stream.read().decode("utf-8").splitlines(),
                change.a_blob.data_stream.read().decode("utf-8").splitlines(),
                lineterm="",
            ):
                output += line + "\n"
        output += "\n"

    return output


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
        db_repo = _get_or_create_repo(db, repo, repo_path)
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


def _get_or_create_repo(db, repo, repo_path):
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


if __name__ == "__main__":
    create_db_and_tables()
    app()
