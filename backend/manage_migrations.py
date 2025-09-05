#!/usr/bin/env python3
"""
Migration management script for TestSpecAI backend.

This script provides convenient commands for managing database migrations.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to handle migration commands."""
    if len(sys.argv) < 2:
        print("Usage: python manage_migrations.py <command>")
        print("Commands:")
        print("  create <message>  - Create a new migration")
        print("  upgrade          - Apply all pending migrations")
        print("  downgrade        - Rollback the last migration")
        print("  current          - Show current migration status")
        print("  history          - Show migration history")
        print("  reset            - Reset database and apply all migrations")
        return

    command = sys.argv[1].lower()

    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: python manage_migrations.py create <message>")
            return
        message = sys.argv[2]
        run_command(f"alembic revision --autogenerate -m \"{message}\"", f"Creating migration: {message}")

    elif command == "upgrade":
        run_command("alembic upgrade head", "Applying migrations")

    elif command == "downgrade":
        run_command("alembic downgrade -1", "Rolling back last migration")

    elif command == "current":
        run_command("alembic current", "Checking current migration status")

    elif command == "history":
        run_command("alembic history", "Showing migration history")

    elif command == "reset":
        print("⚠️  This will delete all data in the database!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            run_command("alembic downgrade base", "Rolling back all migrations")
            run_command("alembic upgrade head", "Applying all migrations")
        else:
            print("Operation cancelled")

    else:
        print(f"Unknown command: {command}")
        print("Use 'python manage_migrations.py' to see available commands")

if __name__ == "__main__":
    main()
