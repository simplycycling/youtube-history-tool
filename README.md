# YouTube Watch History Tool

A Python script to search through your YouTube watch history programmatically.

(README is mostly AI generated)

## Setup with uv

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or see [uv docs](https://docs.astral.sh/uv/))
2. Clone and setup:

   ```bash
   git clone <your-repo>
   cd youtube-history-tool
   uv sync
   ```

3. Set up Google Cloud credentials (TODO: add detailed instructions)
4. Run: uv run youtube-history

## Google Cloud Setup

Before running the tool, you need to set up Google Cloud credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the YouTube Data API v3:
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file
5. Install credentials:
   - Rename the downloaded file to `client_secrets.json` 
   - Place it in your project root directory (same level as README.md)
```
youtube-history-tool/
├── client_secrets.json  ← Your downloaded credentials file
├── README.md
├── pyproject.toml
└── src/
```

### First Run

On your first run, the tool will:
1. 🌐 Open your browser for OAuth authorization  
2. 🔐 Ask you to sign in to Google and grant permissions  
3. 💾 Save your credentials locally for future runs  
4. ✅ Test the API connection:
   ```uv run youtube-history```

### Expected Output

```
🎬 YouTube Watch History Tool
========================================
🔐 Setting up authentication...
Starting OAuth flow...
✅ Authentication successful!
✅ Credentials saved to token.json
✅ Authentication successful!
🎉 YouTube service object created successfully!
📺 Connected as: Your Channel Name
```

## Development

### Running the tool

```
# Run the main script
uv run youtube-history

# Or run the module directly  
uv run python -m youtube_history_tool.main

# Run with development dependencies
uv run --dev python -m youtube_history_tool.main
```

### Adding dependencies

```
# Add a new runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest
```

### Code quality

```
# Format code
uv run black .

# Lint code
uv run ruff check .

# Run tests (when we add them)
uv run pytest
```

## Troubleshooting  

### "Credentials file not found"

- Make sure client_secrets.json is in the project root
- Verify the filename is exactly client_secrets.json

### "Authentication failed"

- Check that YouTube Data API v3 is enabled in Google Cloud Console
- Verify your email is added as a test user in OAuth consent screen
- Try deleting token.json and re-authenticating

### "API test failed"

- This might be normal if OAuth consent screen isn't fully configured
- As long as authentication succeeds, the core functionality should work

### Browser doesn't open for OAuth

- The tool tries to open http://localhost:8080
- You can manually navigate to this URL if needed
- Make sure port 8080 isn't blocked by firewall

## Status
🚧 Work in Progress 🚧

- [x] Basic project structure with uv  
- [x] Google OAuth setup with error handling
- [x] API connection and authentication test 
- [ ] Watch history retrieval
- [ ] Search functionality
- [ ] Export/save results

## Security Notes

- client_secrets.json and token.json are gitignored for security
- Your credentials are stored locally and never shared
- The tool only requests read-only access to your YouTube data
- You can revoke access anytime in Google Account settings

## Next Steps

- Implement watch history retrieval from YouTube API
- Add search and filtering capabilities
- Export results to CSV/JSON
- Add configuration options for advanced users