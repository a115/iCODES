from typer import Typer
from pathlib import Path
from difflib import unified_diff

from loguru import logger
from git import Repo


app = Typer()


def analyse_commit(commit):
    logger.debug(f"Analyzing commit hash: {commit}")
    logger.info(f"Commit summary: {commit.summary}")  # First line of the commit message
    if str(commit.message).strip() != str(commit.summary).strip():
        logger.info(f"Commit message: {commit.message}")
    logger.info(f"Commit author: {commit.author}")
    logger.info(f"Commit date: {commit.authored_datetime}")

    # Get the diff of the commit with its parent
    diff = commit.diff(commit.parents[0])
    for change in diff:
        logger.info(f"Change type: {change.change_type}")
        logger.info(f"Change path: {change.a_path}")
        # logger.info(f"New blob: \n{change.a_blob.data_stream.read().decode('utf-8')}")
        # logger.info(f"Old blob: \n{change.b_blob.data_stream.read().decode('utf-8')}")
        if change.b_blob and change.a_blob:
            logger.info("Diff:")
            for line in unified_diff(
                change.b_blob.data_stream.read().decode("utf-8").splitlines(),
                change.a_blob.data_stream.read().decode("utf-8").splitlines(),
                lineterm="",
            ):
                logger.info(line)


@app.command()
def inspect_repo(repo_path: Path, branch_name: str = ""):
    """
    Inspect a git repository at a given path and branch. If no branch is provided, the current branch is used.
    Logs changes from the latest commit on the branch.
    """
    repo = Repo(repo_path)
    if not branch_name:
        # Get the default branch configured for the repo
        branch_name = repo.active_branch.name
    logger.debug(f"Inspecting repo: {repo_path} on branch: {branch_name}")
    branch = repo.heads[branch_name]

    # Get the commit at the head of the branch
    commit = branch.commit
    analyse_commit(commit)


@app.command()
def build_index(repo_path: Path):
    """
    Build an index of the repository at the given path. NOT YET IMPLEMENTED.
    """
    raise NotImplementedError("Not implemented yet")


if __name__ == "__main__":
    app()
