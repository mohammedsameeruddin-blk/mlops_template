"""Command for adding a new dataset to a project"""

from pathlib import Path
import re
import click
from colorama import Fore, Style

from mlops_cli.core.discovery import ProjectDiscovery
from mlops_cli.core.dataset_generator import DatasetFileGenerator


@click.command(name="add-dataset")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--dataset-name", "-d", required=True, help="Name of the new dataset")
def add_dataset(project_path: str, dataset_name: str):
    """Add a new dataset to a MLOps project"""

    # Validate dataset name format
    if not dataset_name or re.search(r'[^a-zA-Z0-9_-]', dataset_name):
        click.echo(
            f"{Fore.RED}Error: Dataset name must contain only letters, numbers, dashes and underscores.{Style.RESET_ALL}"
        )
        raise click.Abort()

    project_path = Path(project_path)
    discovery = ProjectDiscovery(project_path)

    # Validate project
    if not discovery.is_valid_project():
        click.echo(
            f"{Fore.RED}Error: {project_path} is not a valid mlops project{Style.RESET_ALL}"
        )
        raise click.Abort()

    project_root = discovery.get_project_root()

    click.echo(f"{Fore.CYAN}Analyzing project structure...{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}✓ Project: {project_root.name}{Style.RESET_ALL}\n")

    # Existing datasets (for collision check only)
    existing_datasets = discovery.get_datasets()

    click.echo(
        f"{Fore.CYAN}Existing datasets: "
        f"{', '.join(existing_datasets) if existing_datasets else 'None'}"
        f"{Style.RESET_ALL}\n"
    )

    if dataset_name in existing_datasets:
        click.echo(
            f"{Fore.RED}Error: Dataset '{dataset_name}' already exists{Style.RESET_ALL}"
        )
        raise click.Abort()

    # Generate dataset files (Jinja only)
    generator = DatasetFileGenerator(project_root)

    click.echo(f"{Fore.CYAN}Creating dataset files...{Style.RESET_ALL}")
    updated_files = generator.generate(dataset_name)

    # Report results
    click.echo(
        f"\n{Fore.GREEN}✓ Successfully created new dataset: {dataset_name}{Style.RESET_ALL}\n"
    )
    click.echo(f"{Fore.GREEN}Created files:{Style.RESET_ALL}")
    for file_path in updated_files:
        click.echo(f"  • {file_path.relative_to(project_path)}")

    click.echo(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    click.echo("  1. Review the updated files")
    click.echo("  2. Use the dataset in model training/inference")
