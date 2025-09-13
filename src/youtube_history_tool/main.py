#!/usr/bin/env python3
"""
YouTube Watch History Tool

A simple script to search through your YouTube watch history.
"""

import sys
from pathlib import Path
from .config import SCOPES, DEFAULT_MAX_RESULTS
from .auth import YouTubeAuthenticator
from .history import HistoryRetriever
from .takeout import TakeoutProcessor, find_takeout_files


def main():
    """
    Main entry point for the application
    """
    print("🎬 YouTube Watch History Tool")
    print("=" * 40)

    # Check for Takeout files first
    print("🔍 Checking for Google Takeout files...")
    takeout_files = find_takeout_files()

    if takeout_files:
        print(f"📁 Found {len(takeout_files)} potential Takeout file(s):")
        for i, file_path in enumerate(takeout_files, 1):
            print(f"  {i}. {file_path}")

        use_takeout = input(f"\n🤔 Use Google Takeout data instead of API? (Y/n): ").strip().lower()

        if use_takeout != 'n':
            # Use Takeout data
            if len(takeout_files) == 1:
                selected_file = takeout_files[0]
            else:
                try:
                    choice = int(input(f"Select file (1-{len(takeout_files)}): ")) - 1
                    selected_file = takeout_files[choice]
                except (ValueError, IndexError):
                    print("❌ Invalid selection, using first file")
                    selected_file = takeout_files[0]

            return run_takeout_mode(selected_file)

    # Fall back to API mode
    print("📡 Using YouTube API mode...")
    return run_api_mode()


def run_takeout_mode(file_path: Path):
    """Run in Takeout mode with local data"""
    print(f"\n📂 Loading Google Takeout data from: {file_path}")

    processor = TakeoutProcessor()

    try:
        history = processor.load_watch_history(file_path)
    except Exception as e:
        print(f"❌ Error loading Takeout file: {e}")
        print("💡 Make sure you've downloaded your YouTube data from Google Takeout")
        print("   and extracted the watch-history.json file")
        return

    if not history:
        print("❌ No watch history found in Takeout file")
        return

    # Show summary
    processor.print_summary(history)

    # Show recent items
    print(f"\n🎥 Recent videos (showing up to 15 items):")
    print("-" * 80)
    for item in history[:15]:
        print(f"  {item}")

    # Interactive search
    run_interactive_search(history, processor.search_history)

    # Offer to export
    export = input("\n💾 Export processed history to JSON file? (y/N): ").strip().lower()
    if export in ['y', 'yes']:
        processor.export_to_json(history)


def run_api_mode():
    """Run in API mode with YouTube authentication"""
    # Set up authentication
    print("🔐 Setting up authentication...")
    auth = YouTubeAuthenticator()

    if not auth.authenticate():
        print("\n❌ Authentication failed. Please check your setup:")
        print("1. Download client_secrets.json from Google Cloud Console")
        print("2. Place it in the project root directory")
        print("3. Make sure YouTube Data API v3 is enabled")
        print("\n💡 Alternative: Use Google Takeout for complete watch history")
        print("   Download your data from https://takeout.google.com")
        sys.exit(1)

    print("✅ Authentication successful!")

    # Test API connection
    print("🧪 Testing API connection...")
    try:
        youtube = auth.service
        request = youtube.channels().list(part='snippet', mine=True)
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            channel_name = response['items'][0]['snippet']['title']
            print(f"📺 Connected as: {channel_name}")
        else:
            print("✅ API connection working")

    except Exception as e:
        print(f"⚠️  API test failed: {e}")
        print("Continuing anyway...")

    # Initialize history retriever
    print(f"\n📚 Retrieving activity from YouTube API...")
    retriever = HistoryRetriever(youtube)

    # Get watch history
    history = retriever.get_watch_history(max_results=50)

    if not history:
        print("\n⚠️  No activity retrieved from YouTube API.")
        print("This is normal - YouTube's API provides limited access to watch history.")
        print("\n💡 For complete watch history, try Google Takeout:")
        print("   1. Go to https://takeout.google.com")
        print("   2. Select YouTube data")
        print("   3. Download and extract watch-history.json")
        print("   4. Run this tool again")
        return

    # Show summary
    retriever.print_summary(history)

    # Show recent items
    print(f"\n🎥 Recent activity (showing up to 10 items):")
    print("-" * 60)
    for item in history[:10]:
        print(f"  {item}")

    # Interactive search
    run_interactive_search(history, retriever.search_history)

    # Offer to export
    export = input("\n💾 Export activity to JSON file? (y/N): ").strip().lower()
    if export in ['y', 'yes']:
        retriever.export_to_json(history)


def run_interactive_search(history, search_function):
    """Run interactive search session"""
    print(f"\n🔍 Search functionality:")
    print("Type a search term to find videos, or 'quit' to exit")

    while True:
        try:
            query = input("\nSearch> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue

            results = search_function(query, history)
            if results:
                print(f"\n📋 Found {len(results)} matching videos:")
                for i, item in enumerate(results[:15], 1):
                    print(f"  {i:2d}. {item}")
                if len(results) > 15:
                    print(f"  ... and {len(results) - 15} more")
            else:
                print(f"❌ No videos found matching '{query}'")

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    print("\n👋 Thanks for using YouTube History Tool!")


if __name__ == "__main__":
    main()