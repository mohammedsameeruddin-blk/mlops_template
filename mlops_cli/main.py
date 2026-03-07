"""MLOps CLI Tool - Main entry point"""

import click
from mlops_cli.commands.add_dataset import add_dataset

@click.group()
def cli():
    """Data Science CLI Tool for managing DS projects."""
    pass


cli.add_command(add_dataset)


if __name__ == "__main__":
    cli()