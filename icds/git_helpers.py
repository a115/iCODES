from datetime import datetime
from difflib import unified_diff


CHANGE_TYPES = {
    "A": "Added",
    "D": "Deleted",
    "M": "Modified",
    "R": "Renamed",
}


def should_ignore_change(change) -> bool:
    filename = change.a_path.split("/")[-1]
    to_ignore = ["poetry.lock", "Pipfile.lock"]
    # TODO: Add any further heuristics to ignore certain files or changes that are too big yet low value
    return filename in to_ignore


def extract_commit_info(commit) -> str:
    output = "RepoCommit hash: {commit}\n"
    output += "RepoCommit date: {commit.authored_datetime}\n"
    output += "Author: {commit.author}\n"
    output += "Summary: {commit.summary}\n"
    if str(commit.message).strip() != str(commit.summary).strip():
        output += "Message: {commit.message}\n"

    output += "Changes:\n\n"

    diff = commit.diff(commit.parents[0])
    for change in diff:
        change_diff = format_change_diff(change)
        output += change_diff + "\n"

    return output


def format_change_diff(change) -> str:
    change_str = format_change_str(change)
    change_diff = change_str + "\n"
    if should_ignore_change(change):
        return change_diff
    # logger.info(f"New blob: \n{change.a_blob.data_stream.read().decode('utf-8')}")
    # logger.info(f"Old blob: \n{change.b_blob.data_stream.read().decode('utf-8')}")
    if change.b_blob and change.a_blob:
        for line in unified_diff(
            change.b_blob.data_stream.read().decode("utf-8").splitlines(),
            change.a_blob.data_stream.read().decode("utf-8").splitlines(),
            lineterm="",
        ):
            change_diff += line + "\n"
    return change_diff


def format_change_str(change):
    change_type = CHANGE_TYPES.get(change.change_type, change.change_type)
    change_str = f"{change_type} {change.a_path}"
    if change.change_type == "R":
        change_str += f" -> {change.b_path}"
    return change_str


def get_staged_changes(repo) -> str:
    changes_str = f"Changes as of {datetime.utcnow().isoformat()}: \n\n"
    diff_index = repo.index.diff("HEAD")
    for change in diff_index:
        change_diff = format_change_diff(change)
        changes_str += change_diff + "\n"

    return changes_str
