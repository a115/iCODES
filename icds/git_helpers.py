from difflib import unified_diff


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
