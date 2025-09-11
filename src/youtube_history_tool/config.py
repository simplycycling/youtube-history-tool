"""
Configuration settings for YouTube API access
"""

# OAuth 2.0 scopes - what permissions we're requesting
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly'
]

# File paths
CREDENTIALS_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.json'

# API settings
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Default search parameters
DEFAULT_MAX_RESULTS = 50

# Export settings
DEFAULT_EXPORT_FILENAME = 'watch_history.json'