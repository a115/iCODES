from typer import Typer, echo
from pathlib import Path
from difflib import unified_diff

from loguru import logger
from git import Repo

from llm_interface import analyse_commit

app = Typer()


def extract_commit_info(commit) -> str:
    output = "Commit hash: {commit}\n"
    output += "Commit date: {commit.authored_datetime}\n"
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
def build_index(repo_path: Path):
    """
    Build an index of the repository at the given path. NOT YET IMPLEMENTED.
    """
    raise NotImplementedError("Not implemented yet")


if __name__ == "__main__":
    app()
