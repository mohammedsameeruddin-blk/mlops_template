"""MLOps CLI Tool - Main entry point"""

import click
from mlops_cli.commands.add_dataset import add_dataset
from mlops_cli.commands.add_model import add_model

@click.group()
def cli():
    """Data Science CLI Tool for managing DS projects."""
    pass


cli.add_command(add_dataset)
cli.add_command(add_model)


if __name__ == "__main__":
    cli()