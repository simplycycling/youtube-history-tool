"""
OAuth 2.0 authentication for YouTube API
"""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE, API_SERVICE_NAME, API_VERSION


class YouTubeAuthenticator:
    """Handles OAuth 2.0 authentication for YouTube API"""

    def __init__(self, credentials_file=CREDENTIALS_FILE, token_file=TOKEN_FILE):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self._service = None

    def authenticate(self):
        """
        Authenticate with YouTube API using OAuth 2.0
        Returns True if successful, False otherwise
        """
        creds = None

        # Load existing token if available
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                print(f"Warning: Could not load existing token: {e}")
                creds = None

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    creds = None

            if not creds:
                # Check if credentials file exists
                if not self.credentials_file.exists():
                    print(f"❌ Credentials file not found: {self.credentials_file}")
                    print("Please download client_secrets.json from Google Cloud Console")
                    return False

                print("Starting OAuth flow...")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    creds = flow.run_local_server(port=8080)
                    print("✅ Authentication successful!")
                except Exception as e:
                    print(f"❌ Authentication failed: {e}")
                    return False

            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                print(f"✅ Credentials saved to {self.token_file}")
            except Exception as e:
                print(f"Warning: Could not save token: {e}")

        # Build the service
        try:
            self._service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            return True
        except Exception as e:
            print(f"❌ Failed to build YouTube service: {e}")
            return False

    @property
    def service(self):
        """Get the authenticated YouTube service object"""
        if self._service is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return self._service

    def is_authenticated(self):
        """Check if we have a valid service connection"""
        return self._service is not None


def get_youtube_service():
    """
    Convenience function to get an authenticated YouTube service
    Returns None if authentication fails
    """
    auth = YouTubeAuthenticator()
    if auth.authenticate():
        return auth.service
    return None