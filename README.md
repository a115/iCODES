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

## Usage

To analyze a Git repository with iCODES, run the following command:

    poetry run icodes analyze /path/to/repo

This will generate an indexed database of commit insights. You can then start the iCODES search server:

    poetry run icodes serve

Open your web browser and navigate to `http://localhost:8000` to access the iCODES search interface.


## Contributing

We welcome contributions to iCODES!
