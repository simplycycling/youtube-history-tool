#!/usr/bin/env python3
"""
YouTube Watch History Tool

A simple script to search through your YouTube watch history.
"""

import sys
from .config import SCOPES, DEFAULT_MAX_RESULTS
from .auth import YouTubeAuthenticator


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

    # TODO: Implement API connection test
    print("[ ] Testing API connection...")

    # TODO: Implement history retrieval
    print("[ ] Retrieving watch history...")

    # TODO: Implement search functionality
    print("[ ] Adding search capabilities...")

    print(f"\n🚧 Next steps: implement API calls")
    print(f"Configured scopes: {', '.join(SCOPES)}")

    try:
        # Quick test to see if we can make API calls
        youtube = auth.service
        print("🎉 YouTube service object created successfully!")

        # Test with a simple API call
        request = youtube.channels().list(part='snippet', mine=True)
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            channel_name = response['items'][0]['snippet']['title']
            print(f"📺 Connected as: {channel_name}")
        else:
            print("✅ API connection working (no channel info available)")

    except Exception as e:
        print(f"⚠️  API test failed: {e}")
        print("This might be normal if you haven't set up the OAuth consent screen properly")


if __name__ == "__main__":
    main()