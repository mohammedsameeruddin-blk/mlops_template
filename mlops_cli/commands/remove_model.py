"""Command for removing an existing model from a project"""

from pathlib import Path
import re
import click
from colorama import Fore, Style

from mlops_cli.core.discovery import ProjectDiscovery
from mlops_cli.core.model_degenerator import ModelFileDegenerator


@click.command(name="remove-model")
@click.argument("project_path", type=click.Path(exists=True))
@click.option("--model-name", "-m", required=True, help="Name of the model to remove")
def remove_model(project_path: str, model_name: str):
    """Remove an existing model from a MLOps project"""

    # Validate model name format
    if not model_name or re.search(r"[^a-zA-Z0-9_-]", model_name):
        click.echo(
            f"{Fore.RED}Error: Model name must contain only letters, numbers, dashes and underscores.{Style.RESET_ALL}"
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

    existing_models = discovery.get_models()

    click.echo(
        f"{Fore.CYAN}Existing models: "
        f"{', '.join(existing_models) if existing_models else 'None'}"
        f"{Style.RESET_ALL}\n"
    )

    if model_name not in existing_models:
        click.echo(
            f"{Fore.RED}Error: Model '{model_name}' does not exist{Style.RESET_ALL}"
        )
        raise click.Abort()

    degenerator = ModelFileDegenerator(project_root)
    click.echo(f"{Fore.CYAN}Removing model '{model_name}'...{Style.RESET_ALL}")
    removed_files, updated_workflow_files = degenerator.degenerate(model_name)

    click.echo(
        f"\n{Fore.GREEN}✓ Successfully removed model: {model_name}{Style.RESET_ALL}\n"
    )

    click.echo(f"{Fore.GREEN}Removed files:{Style.RESET_ALL}")
    for file_path in removed_files:
        click.echo(f"  • {file_path.relative_to(project_path)}")

    click.echo(f"\n{Fore.GREEN}Updated workflow files:{Style.RESET_ALL}")
    for file_path in updated_workflow_files:
        click.echo(f"  • {file_path.relative_to(project_path)}")
