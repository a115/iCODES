from typer import Typer, echo
from pathlib import Path
from difflib import unified_diff

from loguru import logger
from git import Repo

from settings import settings


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


def analyse_commit(commit_info: str) -> tuple[str, str]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    model = "gpt-3.5-turbo"

    system_prompt = """
    You are an experienced software engineer reviewing a commit on a git repository. Please carefully analyse the 
    commit and provide a summary of the key changes. Try your best to also infer the intent behind the changes, given 
    the available context. 
    """  # TODO: Chuck the project's README in here for context?

    prompt = (
        "Please summarise the key changes in this commit and infer the intent behind the changes: "
        + commit_info
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    analysis = response.choices[0].message.content

    # Call the LLM one more time to summarise the analysis into a single line that can be used as an improved commit message
    summarise_prompt = "Please summarise this analysis into a single line that can be used as an improved commit message. "

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": analysis},
        {"role": "user", "content": summarise_prompt},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    summary = response.choices[0].message.content

    return analysis, summary


@app.command()
def inspect_repo(repo_path: Path, branch_name: str = "", n_commits: int = 10):
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
        echo(analysis + "\n")
        echo("Summary: " + summary)


@app.command()
def build_index(repo_path: Path):
    """
    Build an index of the repository at the given path. NOT YET IMPLEMENTED.
    """
    raise NotImplementedError("Not implemented yet")


if __name__ == "__main__":
    app()
