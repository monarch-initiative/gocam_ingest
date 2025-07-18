# gocam_ingest

| [Documentation](https://monarch-initiative.github.io/gocam_ingest) |

A repository for transforming GOCAM models to Knowledge Graph nodes and edges.

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)
- [Cruft](https://cruft.github.io/cruft/#installation) (optional)


# Setting Up a New Project -- Delete this section when completed

Upon creating a new project from the `cookiecutter-monarch-ingest` template, you can install and test the project:

```bash
cd gocam_ingest
make install
make test
```

There are a few additional steps to complete before the project is ready for use.

#### GitHub Repository

1. Create a new repository on GitHub.
1. Enable GitHub Actions to read and write to the repository (required to deploy the project to GitHub Pages).
   - in GitHub, go to Settings -> Action -> General -> Workflow permissions and choose read and write permissions
1. Initialize the local repository and push the code to GitHub. For example:

   ```bash
   cd gocam_ingest
   git init
   git remote add origin https://github.com/<username>/<repository>.git
   git add -A && git commit -m "Initial commit"
   git push -u origin main
   ```

#### Transform Code and Configuration

1. Edit the `download.yaml`, `transform.py`, `transform.yaml`, and `metadata.yaml` files to suit your needs.
   - For more information, see the [Koza documentation](https://koza.monarchinitiative.org) and [kghub-downloader](https://github.com/monarch-initiative/kghub-downloader).
1. Add any additional dependencies to the `pyproject.toml` file.
1. Adjust the contents of the `tests` directory to test the functionality of your transform.

#### Documentation

1. Update this `README.md` file with any additional information about the project.
1. Add any appropriate documentation to the `docs` directory.

> **Note:** After the GitHub Actions for deploying documentation runs, the documentation will be automatically deployed to GitHub Pages.  
> However, you will need to go to the repository settings and set the GitHub Pages source to the `gh-pages` branch, using the `/docs` directory.

Once you have completed these steps, you can remove the [Setting Up a New Project](#setting-up-a-new-project) section from this `README.md` file.

## TODO/Roadmap

- **GOCAM Ingest Implementation**
  - Get list of available models from: https://live-go-cam.geneontology.io/product/json/provider-to-model.json
  - Retrieve model details from: https://live-go-cam.geneontology.io/product/yaml/go-cam/[MODEL_INTERNAL_ID].yaml
  - Example model: https://live-go-cam.geneontology.io/product/yaml/go-cam/ZFIN_ZDB-GENE-031006-12.yaml

## Data Sources

GOCAM (Gene Ontology Causal Activity Models) data is available from the Gene Ontology Consortium through their live GO-CAM portal.

### Source Files
This ingest uses dynamic data retrieval from the GO-CAM API endpoints:
  - **Model List**: https://live-go-cam.geneontology.io/product/json/provider-to-model.json - Provides a comprehensive list of available GOCAM models with their internal IDs
  - **Model Details**: https://live-go-cam.geneontology.io/product/yaml/go-cam/[MODEL_INTERNAL_ID].yaml - Contains detailed YAML representation of each GOCAM model including molecular functions, biological processes, and causal relationships

### Nodes and Edges
The ingest transforms GOCAM models into Knowledge Graph format:
 - **Gene/Protein Nodes** - Molecular entities participating in biological processes with GO molecular function annotations
 - **Biological Process Nodes** - GO biological process terms represented in the models
 - **Molecular Function Nodes** - GO molecular function terms associated with gene products
 - **Causal Activity Edges** - Represents causal relationships between molecular activities and biological processes as defined in GOCAM models

## Transform Code and Configuration
Metadata for the infest is in the `metadata.yaml` file and may require some adjustment depending on your configuration. Data files and locations are listed in the `download.yaml` file which is used to download all of the data sources before the transform. The `transform.yaml` file and python file `transform.py` contain the configuration and transformation code, respectively. 

For more information, see the [Koza documentation](https://koza.monarchinitiative.org) and [kghub-downloader](https://github.com/monarch-initiative/kghub-downloader).

Dependencies are listed in `pyproject.toml` file. This project uses pytest for development testing located in the `tests` directory to test the functionality of your transform.

## Documentation
The documentation for this ingest is in this `README.md` file and additional documentation is in the `docs` directory.

> **Note:** After the GitHub Actions for deploying documentation runs, the documentation will be automatically deployed to GitHub Pages.  

#### GitHub Actions

This project is set up with several GitHub Actions workflows.
You should not need to modify these workflows unless you want to change the behavior.
The workflows are located in the `.github/workflows` directory:

- `test.yaml`: Run the pytest suite.
- `create-release.yaml`: Create a new release once a week, or manually.
- `deploy-docs.yaml`: Deploy the documentation to GitHub Pages (on pushes to main).
- `update-docs.yaml`: After a release, update the documentation with node/edge reports.

## Installation

```bash
cd gocam_ingest
make install
# or
poetry install
```

> **Note** that the `make install` command is just a convenience wrapper around `poetry install`.

Once installed, you can check that everything is working as expected:

```bash
# Run the pytest suite
make test
# Download GOCAM models (this will take several hours for complete download)
poetry run ingest download
# Run the Koza transform
poetry run ingest transform
```

## Usage

This project is set up with a Makefile for common tasks.  
To see available options:

```bash
make help
```

### Download and Transform

#### Downloading GOCAM Models

The download process fetches GOCAM models from the Gene Ontology Consortium's live API:

```bash
poetry run ingest download
```

This command:
- Fetches the complete list of available models (~51,000 models) from the provider API
- Downloads each model's YAML file with a 1-second delay between requests for rate limiting
- Saves files to `data/gocam_models/` directory
- Handles 404 errors gracefully for non-existent models
- Skips already downloaded files, making the process resumable

**Note:** The complete download takes several hours due to the large number of models and rate limiting. The process can be interrupted and resumed safely.

#### Running the Transform

To run the Koza transform for gocam_ingest:

```bash
poetry run ingest transform
```

To see available options:

```bash
poetry run ingest download --help
# or
poetry run ingest transform --help
```

### Testing

To run the test suite:

```bash
make test
```

---

> This project was generated using [monarch-initiative/cookiecutter-monarch-ingest](https://github.com/monarch-initiative/cookiecutter-monarch-ingest).  
> Keep this project up to date using cruft by occasionally running in the project directory:
>
> ```bash
> cruft update
> ```
>
> For more information, see the [cruft documentation](https://cruft.github.io/cruft/#updating-a-project)
