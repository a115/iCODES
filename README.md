# iCODES: LLM-powered Git archeology
## a.k.a. Intelligent Commit Ontology Distiller and Enhanced Search

iCODES is an innovative tool that leverages LLM techniques to analyse and index Git commit histories in context. By intelligently summarizing commit intents and enabling powerful semantic search, iCODES empowers developers to understand and navigate codebases more efficiently. 

## Features

* Intelligent commit analysis powered by large language models
* Semantic search (coming soon) to find relevant commits and code changes
* Flexible search options to filter by author, file path, and date range
* Commit timeline visualisation
* Insight extraction to identify trends and patterns in code evolution
* CLI and web-based UI (comming soon)

## Installation

iCODES requires Python 3.11 or higher. 

    pip install icodes

Since the only supported LLM backend right now is OpenAI, you will need to export your OpenAI API key to the environment variable `OPENAI_API_KEY`. You can also set the `DEFAULT_MODEL` environment variable to the GPT model you wish to use (default value is "gpt-3.5-turbo" for a reasonable price / quality ratio.)

### Alternative installation 

Or clone the repo:

    git clone https://github.com/a115/iCODES.git

It is recommended to use Poetry for dependency management. To install the dependencies, run: 

    poetry install

If this method is used, prefix all commands with `poetry run python icodes.py` (instead of `icodes`) to run the iCODES commands.

## Usage

### Inspecting a Repository

To inspect a repository with iCODES, run:

    icodes inspect-repo /path/to/repo [--branch-name BRANCH_NAME]

Replace /path/to/repo with the path to the Git repository you want to analyse. You can optionally specify a branch name using the --branch-name flag. If no branch is provided, iCODES will use the current branch for the repository.

iCODES will analyse the latest commit on the specified branch and log the changes.


### Building an Index

To build an index for a Git repository with iCODES, run the following command:

    icodes build-index <path-to-repo>

This will generate an indexed database of commit insights. 

### Searching Commits

iCODES provides a powerful search interface to find relevant commits based on various criteria. To search the indexed commit data, use the following command:

    icodes search <query> [--author AUTHOR] [--file FILE] [--start-date START_DATE] [--end-date END_DATE]

- `<query>`: The search query string to match against commit messages and details.
- `--author AUTHOR`: Filter commits by the specified author.
- `--file FILE`: Filter commits that modified the specified file path.
- `--start-date START_DATE`: Filter commits after the specified date (YYYY-MM-DD).
- `--end-date END_DATE`: Filter commits before the specified date (YYYY-MM-DD).

Example usage:

    icodes search "bug fix" --author "Jane Doe" --file "src/main.py" --start-date "2023-01-01" --end-date "2023-12-31"

This command will search for commits containing the phrase "bug fix" authored by "John Doe", modifying the file "src/main.py", between the dates "2023-01-01" and "2023-12-31".

### Suggesting a commit for the currently staged changes

You can now use the `suggest-commit-message` command to analyse the currently staged changes and suggest a commit message:

    icodes suggest_commit_message /path/to/repo

This command will retrieve the staged changes, format them into a commit-like format, and then use the LLM to analyse the changes and suggest a commit message.

The suggested commit message and the detailed analysis will be displayed in the console output.


## Contributing

We welcome contributions to iCODES!
