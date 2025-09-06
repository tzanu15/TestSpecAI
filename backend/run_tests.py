#!/usr/bin/env python3
"""
Test runner script for TestSpecAI backend tests.

This script provides a convenient way to run tests with different configurations
and generate reports for the TestSpecAI backend API endpoints.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="TestSpecAI Backend Test Runner")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests with verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests (skip slow tests)"
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run only API tests"
    )
    parser.add_argument(
        "--specific",
        type=str,
        help="Run specific test file or function"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean test artifacts before running"
    )

    args = parser.parse_args()

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("🚀 TestSpecAI Backend Test Runner")
    print(f"📁 Working directory: {backend_dir}")

    # Clean test artifacts if requested
    if args.clean:
        clean_commands = [
            "rm -rf .pytest_cache",
            "rm -rf htmlcov",
            "rm -rf .coverage",
            "rm -f test.db",
            "find . -name '*.pyc' -delete",
            "find . -name '__pycache__' -type d -exec rm -rf {} +"
        ]

        for cmd in clean_commands:
            run_command(cmd, f"Cleaning: {cmd}")

    # Build pytest command
    pytest_cmd = ["pytest"]

    # Add coverage if requested
    if args.coverage or args.html_coverage:
        pytest_cmd.extend(["--cov=app", "--cov-report=term-missing"])
        if args.html_coverage:
            pytest_cmd.append("--cov-report=html")

    # Add verbose output if requested
    if args.verbose:
        pytest_cmd.append("-v")

    # Add fast test filter if requested
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])

    # Add API-only filter if requested
    if args.api_only:
        pytest_cmd.append("tests/test_api/")

    # Add specific test if requested
    if args.specific:
        pytest_cmd.append(args.specific)

    # Add parallel execution if requested
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])

    # Add additional options
    pytest_cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])

    # Run the tests
    command = " ".join(pytest_cmd)
    success = run_command(command, "Running tests")

    if success:
        print("\n🎉 All tests completed successfully!")

        # Show coverage summary if coverage was run
        if args.coverage or args.html_coverage:
            print("\n📊 Coverage Summary:")
            if args.html_coverage:
                print("📄 HTML coverage report generated in htmlcov/index.html")

            # Show coverage summary
            run_command("coverage report", "Coverage report")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
