#!/usr/bin/env python3
"""
YouTube Watch History Tool

A simple script to search through your YouTube watch history.
"""

import sys
from .config import SCOPES, DEFAULT_MAX_RESULTS
from .auth import YouTubeAuthenticator
from .history import HistoryRetriever


def main():
    """
    Main entry point for the application
    """
    print("🎬 YouTube Watch History Tool")
    print("=" * 40)

    # Set up authentication
    print("🔐 Setting up authentication...")
    auth = YouTubeAuthenticator()

    if not auth.authenticate():
        print("\n❌ Authentication failed. Please check your setup:")
        print("1. Download client_secrets.json from Google Cloud Console")
        print("2. Place it in the project root directory")
        print("3. Make sure YouTube Data API v3 is enabled")
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
    print(f"\n📚 Retrieving watch history...")
    retriever = HistoryRetriever(youtube)

    # Get watch history
    history = retriever.get_watch_history(max_results=50)

    if not history:
        print("\n⚠️  No watch history retrieved.")
        print("This could be due to:")
        print("  - YouTube API limitations on watch history access")
        print("  - Your privacy settings")
        print("  - No recent activity in the types we can access")
        print("\nNote: YouTube's API provides limited access to watch history for privacy reasons.")
        return

    # Show summary
    retriever.print_summary(history)

    # Show recent items
    print(f"\n🎥 Recent activity (showing up to 10 items):")
    print("-" * 60)
    for item in history[:10]:
        print(f"  {item}")

    # Interactive search
    print(f"\n🔍 Search functionality:")
    print("Type a search term to find videos, or 'quit' to exit")

    while True:
        try:
            query = input("\nSearch> ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if not query:
                continue

            results = retriever.search_history(query, history)
            if results:
                print(f"\n📋 Found {len(results)} matching videos:")
                for i, item in enumerate(results[:10], 1):
                    print(f"  {i}. {item}")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more")
            else:
                print(f"❌ No videos found matching '{query}'")

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    # Offer to export
    export = input("\n💾 Export history to JSON file? (y/N): ").strip().lower()
    if export in ['y', 'yes']:
        retriever.export_to_json(history)

    print("\n👋 Thanks for using YouTube History Tool!")


if __name__ == "__main__":
    main()