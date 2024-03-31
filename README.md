# Intelligent Commit Ontology Distiller and Enhanced Search (iCODES)

iCODES is an innovative tool that leverages LLM techniques to analyse and index Git commit histories in context. By intelligently summarizing commit intents and enabling powerful semantic search, iCODES empowers developers to understand and navigate codebases more efficiently. 

## Features

* Intelligent commit analysis powered by large language models
* Semantic search to find relevant commits and code changes
* Commit timeline visualisation
* Insight extraction to identify trends and patterns in code evolution
* CLI and web-based UI

## Installation

iCODES requires Python 3.11 or higher. It is recommended to use Poetry for dependency management. 

To install the dependencies, run: 

    poetry install


## Usage

To inspect a repository with iCODES, run:

    poetry run python icodes.py inspect-repo /path/to/repo [--branch-name BRANCH_NAME]

Replace /path/to/repo with the path to the Git repository you want to analyze. You can optionally specify a branch name using the --branch-name flag. If no branch is provided, iCODES will use the current branch for the repository.

iCODES will analyze the latest commit on the specified branch and log the changes.

To build an index for a Git repository with iCODES, run the following command:

    poetry run python icodes.py build-index <path-to-repo>

This will generate an indexed database of commit insights. You can then start the iCODES search server:

    poetry run icodes serve

Open your web browser and navigate to `http://localhost:8000` to access the iCODES search interface.


## Contributing

We welcome contributions to iCODES!
