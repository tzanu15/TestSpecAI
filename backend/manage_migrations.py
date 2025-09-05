#!/usr/bin/env python3
"""
Migration management script for TestSpecAI backend.
"""
import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def create_migration(message):
    """Create a new migration."""
    print(f"Creating migration: {message}")
    return run_command(f"alembic revision --autogenerate -m \"{message}\"")

def upgrade_database():
    """Upgrade database to latest migration."""
    print("Upgrading database to latest migration...")
    return run_command("alembic upgrade head")

def downgrade_database(revision="base"):
    """Downgrade database to specified revision."""
    print(f"Downgrading database to revision: {revision}")
    return run_command(f"alembic downgrade {revision}")

def show_current():
    """Show current migration status."""
    print("Current migration status:")
    return run_command("alembic current")

def show_history():
    """Show migration history."""
    print("Migration history:")
    return run_command("alembic history")

def main():
    """Main function to handle migration commands."""
    if len(sys.argv) < 2:
        print("Usage: python manage_migrations.py <command> [args]")
        print("Commands:")
        print("  create <message>  - Create a new migration")
        print("  upgrade          - Upgrade to latest migration")
        print("  downgrade [rev]  - Downgrade to revision (default: base)")
        print("  current          - Show current migration status")
        print("  history          - Show migration history")
        return

    command = sys.argv[1].lower()

    if command == "create":
        if len(sys.argv) < 3:
            print("Error: Migration message required")
            return
        message = sys.argv[2]
        create_migration(message)
    elif command == "upgrade":
        upgrade_database()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "base"
        downgrade_database(revision)
    elif command == "current":
        show_current()
    elif command == "history":
        show_history()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
