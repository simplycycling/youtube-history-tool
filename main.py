#!/usr/bin/env python3
"""
YouTube Watch History Tool

A simple script to search through your YouTube watch history.
Currently just a placeholder that will be built out incrementally.
"""

import sys
from .config import SCOPES, DEFAULT_MAX_RESULTS


def main():
    """
    Main entry point for the application
    """
    print("🎬 YouTube Watch History Tool")
    print("=" * 40)

    # TODO: Implement OAuth authentication
    print("[ ] Setting up authentication...")

    # TODO: Implement API connection
    print("[ ] Connecting to YouTube API...")

    # TODO: Implement history retrieval
    print("[ ] Retrieving watch history...")

    # TODO: Implement search functionality  
    print("[ ] Adding search capabilities...")

    print("\n🚧 Coming soon! This is just the initial structure.")
    print(f"Configured scopes: {', '.join(SCOPES)}")
    print(f"Default max results: {DEFAULT_MAX_RESULTS}")


if __name__ == "__main__":
    main()