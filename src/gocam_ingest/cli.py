"""Command line interface for gocam_ingest."""
import logging
import time
import json
from pathlib import Path

import requests
import typer

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.callback()
def callback(version: bool = typer.Option(False, "--version", is_eager=True),
):
    """gocam_ingest CLI."""
    if version:
        from gocam_ingest import __version__
        typer.echo(f"gocam_ingest version: {__version__}")
        raise typer.Exit()


def download_gocam_models(output_dir: Path = Path("data/gocam_models")):
    """Download GOCAM model files from the GO-CAM API."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    provider_url = "https://live-go-cam.geneontology.io/product/json/provider-to-model.json"
    model_base_url = "https://live-go-cam.geneontology.io/product/yaml/go-cam"
    
    typer.echo(f"Fetching model list from {provider_url}")
    
    try:
        response = requests.get(provider_url)
        response.raise_for_status()
        provider_data = response.json()
        
        all_model_ids = []
        for provider, model_ids in provider_data.items():
            all_model_ids.extend(model_ids)
        
        typer.echo(f"Found {len(all_model_ids)} models to download")
        
        for i, model_id in enumerate(all_model_ids, 1):
            model_url = f"{model_base_url}/{model_id}.yaml"
            output_file = output_dir / f"{model_id}.yaml"
            
            if output_file.exists():
                typer.echo(f"[{i}/{len(all_model_ids)}] Skipping {model_id} (already exists)")
                continue
                
            typer.echo(f"[{i}/{len(all_model_ids)}] Downloading {model_id}")
            
            try:
                model_response = requests.get(model_url)
                model_response.raise_for_status()
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(model_response.text)
                    
            except requests.RequestException as e:
                typer.echo(f"Error downloading {model_id}: {e}")
                continue
            
            time.sleep(1)
        
        typer.echo(f"Download complete. Models saved to {output_dir}")
        
    except requests.RequestException as e:
        typer.echo(f"Error fetching model list: {e}")
        raise typer.Exit(1)


@app.command()
def download(force: bool = typer.Option(False, help="Force download of data, even if it exists")):
    """Download GOCAM models."""
    typer.echo("Downloading GOCAM models...")
    download_gocam_models()


@app.command()
def transform(
    output_dir: str = typer.Option("output", help="Output directory for transformed data"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    verbose: int = typer.Option(False, help="Whether to be verbose"),
):
    """Run the Koza transform for gocam_ingest."""
    from koza.cli_utils import transform_source
    
    typer.echo("Transforming data for gocam_ingest...")
    transform_code = Path(__file__).parent / "transform.yaml"
    transform_source(
        source=transform_code,
        output_dir=output_dir,
        output_format="tsv",
        row_limit=row_limit,
        verbose=verbose,
    )
    

if __name__ == "__main__":
    app()
