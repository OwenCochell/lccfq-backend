"""
CLI commands for user management.
"""

import typer

from pathlib import Path
from typing import Annotated

from lccfq_backend.config import BackendSettings
from lccfq_backend.backend.users import UserManager, JSONSerialize
from lccfq_backend.model.user import User, Permissions

user_app = typer.Typer(
    name="user",
    help="User Management Commands",
)

def init_users(config_file: str):
    """Initialize the user management system
    """

    config_path = Path(config_file)
    try:
        config = BackendSettings(_toml_file=config_path)
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        typer.echo(f"Please place a config file at {config_path}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error loading configuration: {e}", err=True)
        raise typer.Exit(1)

    # Create and load the user manager

    user_manager = UserManager()
    json_serializer = JSONSerialize(file_path=config.user_file)

    try:

        json_serializer.load(user_manager)

    except Exception as e:
        typer.echo(f"Failed to load user data: {e}. Starting with empty user manager.", err=True)
    
    return user_manager, json_serializer

@user_app.command()
def add(name: str):
    """Add a new user with the given name.
    """

    user_manager, json_serializer = init_users(config_file="config.toml")

    try:

        user_manager.create_user(name=name, perms=Permissions(0))

        json_serializer.dump(user_manager)
        typer.echo(f"User '{name}' added successfully.")
    except Exception as e:
        typer.echo(f"Error adding user: {e}", err=True)
        raise typer.Exit(1)

@user_app.command("list")
def list_user():
    """List all users.
    """

    user_manager, _ = init_users(config_file="config.toml")

    typer.echo("Users:")
    for user in user_manager.users:
        typer.echo(f"  - {user}")

@user_app.command()
def info(name: str):
    """Show information about a specific user.
    """

    user_manager, _ = init_users(config_file="config.toml")

    # Get the user from the manager

    user = user_manager.get_user(name)

    if user:
        typer.echo(f"User: {user.name}")
        typer.echo(f"  ID: {user.id}")
        typer.echo(f"  Permissions: {user.perms}")
        typer.echo(f"  Groups: {[group.name for group in user.groups]}")
    else:
        typer.echo(f"User '{name}' not found.", err=True)
        raise typer.Exit(1)

@user_app.command()
def list_perms():
    """List all available permissions.
    """

    typer.echo("Available Permissions:")
    for perm in Permissions:
        typer.echo(f"  - {perm.name} (value: {perm.value})")

@user_app.command()
def add_perms(name: str, perms: Annotated[list[Permissions], typer.Option()]):
    """Add permissions to a user.
    """

    user_manager, json_serializer = init_users(config_file="config.toml")

    # Does the user exist?

    if not user_manager.has_user(name):
        typer.echo(f"User '{name}' not found.", err=True)
        raise typer.Exit(1)

    # Add the specified permissions to the user

    for perm_name in perms:
        try:

            user_manager.add_permission(name, Permissions(perm_name))
        except KeyError:
            typer.echo(f"Permission '{perm_name}' not found.", err=True)
            raise typer.Exit(1)

    # Save the updated user manager

    json_serializer.dump(user_manager)
    typer.echo(f"Permissions {perms} added to user '{name}' successfully.")
