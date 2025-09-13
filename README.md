# YouTube Watch History Tool

A Python script to search through your YouTube watch history programmatically. Works with both Google Takeout data (recommended) and YouTube API.

(README written by Claude.ai)

## Quick Start

### Option 1: Google Takeout (Recommended - Complete History)

1. **Get your data**: Download from [Google Takeout](https://takeout.google.com)
2. **Setup tool**: `uv sync`
3. **Run**: `uv run youtube-history`

### Option 2: YouTube API (Limited Recent Activity)

1. **Setup Google Cloud credentials** (see below)
2. **Setup tool**: `uv sync`
3. **Run**: `uv run youtube-history`

## Installation

### Prerequisites

- **uv package manager**: `curl -LsSf https://astral.sh/uv/install.sh | sh` ([docs](https://docs.astral.sh/uv/))

### Setup

```bash
git clone <your-repo>
cd youtube-history-tool
uv sync
```

## Google Takeout Setup (Recommended)

Google Takeout provides your **complete** YouTube watch history going back years, while the YouTube API only provides limited recent activity.

### 1. Download Your Data

1. Go to [Google Takeout](https://takeout.google.com)
2. **Deselect all**, then select only **"YouTube and YouTube Music"**
3. Click **"Multiple formats"** and choose:

- **History**: JSON format (recommended)

4. **Create export** and wait for email notification (can take hours/days for large histories)
5. **Download** the archive when ready

### 2. Extract Watch History

1. **Extract** the downloaded archive
2. **Navigate to**: `Takeout/YouTube and YouTube Music/history/`
3. **Find**: `watch-history.json`
4. **Copy** this file to your project directory:

```
youtube-history-tool/
├── watch-history.json    ← Your complete watch history
├── README.md
├── pyproject.toml
└── src/
```

### 3. Run the Tool

The tool will **automatically detect** your Takeout file and offer to use it!

**Expected output with Takeout:**

```
🎬 YouTube Watch History Tool
========================================
🔍 Checking for Google Takeout files...
📁 Found 1 potential Takeout file(s):
  1. ./watch-history.json

🤔 Use Google Takeout data instead of API? (Y/n):

📂 Loading Google Takeout data from: watch-history.json
📥 Loaded 15,847 raw entries from Takeout
✅ Processed 15,234 valid watch history items

📊 Google Takeout Watch History Summary
==================================================
Total videos watched: 15,234
Date range: 2018-03-15 to 2024-12-08
Time span: 2,459 days
Average videos per day: 6.2

Top 10 watched channels:
   1. Veritasium: 342 videos (2.2%)
   2. 3Blue1Brown: 287 videos (1.9%)
   3. Kurzgesagt: 201 videos (1.3%)
   ...
```

## YouTube API Setup (Fallback)

If you don't have Takeout data or want to test API functionality:

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one

### 2. Enable YouTube Data API

1. Go to **"APIs & Services" > "Library"**
2. Search for **"YouTube Data API v3"** and enable it

### 3. Configure OAuth Consent Screen

1. Go to **"APIs & Services" > "OAuth consent screen"**
2. Choose **"External"** (unless you have Google Workspace)
3. Fill in required fields and add your email as a test user

### 4. Create OAuth Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. **"Create Credentials" > "OAuth client ID"**
3. Choose **"Desktop application"**
4. Download the JSON file as `client_secrets.json`
5. Place in project root

## Features

### 🔍 Search & Filter

- Search by video title, channel name, or description
- Interactive search with real-time results
- Case-insensitive matching

### 📊 Analytics & Statistics

- **Complete viewing history** (with Takeout)
- **Date range analysis** (first to last watched video)
- **Top channels** with watch counts and percentages
- **Daily viewing averages**
- **Timeline statistics**

### 💾 Export Options

- **JSON export** for further analysis
- **Structured data** with video IDs, URLs, timestamps
- **Compatible** with data analysis tools

### 🛡️ Privacy & Security

- **Local processing only** - your data never leaves your machine
- **Credentials stored locally** and gitignored
- **Read-only access** to your YouTube data
- **Revoke access anytime** in [Google Account settings](https://myaccount.google.com/permissions)

## Usage Examples

### Basic Search

```
uv run youtube-history
# Follow prompts, then:
Search> python tutorial
Search> veritasium
Search> quit
```

### Find Specific Content

```
Search> machine learning      # Find ML videos
Search> music                 # Find music videos
Search> 2023                  # Find videos from 2023 (in titles)
```

## Data Comparison: Takeout vs API

| Feature              | Google Takeout         | YouTube API                       |
| -------------------- | ---------------------- | --------------------------------- |
| **History depth**    | Complete (years)       | Limited (recent)                  |
| **Data accuracy**    | Actual watched videos  | Uploads/playlists/recommendations |
| **Volume**           | 10,000+ videos typical | ~50 items max                     |
| **Timestamps**       | Precise watch times    | Activity timestamps               |
| **Setup complexity** | Simple download        | OAuth configuration               |
| **Rate limits**      | None                   | Yes (API quotas)                  |
| **Privacy**          | Complete control       | Google's API policies             |

**Recommendation**: Use Google Takeout for complete history analysis, API for recent activity monitoring.

## Development

### Running the Tool

```
# Main script
uv run youtube-history

# Module mode
uv run python -m youtube_history_tool.main

# With development dependencies
uv run --dev python -m youtube_history_tool.main
```

### Adding Dependencies

```
uv add requests              # Runtime dependency
uv add --dev pytest          # Development dependency
```

### Code Quality

```
uv run black .               # Format code
uv run ruff check .          # Lint code
uv run pytest                # Run tests (when added)
```

## Troubleshooting

### Takeout Issues

**"No Takeout files found"**

- Ensure `watch-history.json` is in the project root
- Check the exact filename (case-sensitive)
- Verify the file isn't empty or corrupted

**"Error loading Takeout file"**

- Make sure the file is valid JSON
- Check if you downloaded the right file (`watch-history.json`, not `search-history.json`)
- Try re-downloading from Google Takeout

### API Issues

**"Credentials file not found"**

- Verify `client_secrets.json` is in project root
- Check filename exactly matches

**"Access blocked" during OAuth**

- Add your email as a test user in OAuth consent screen
- Go to Google Cloud Console → "APIs & Services" → "OAuth consent screen" → "Test users"

**"No watch history retrieved"**

- This is normal - YouTube API has limited watch history access
- Use Google Takeout for complete history

### General Issues

**"No videos found" in search**

- Check spelling and try broader terms
- Remember search is case-insensitive but exact substring matching
- Try searching channel names instead of video titles

## File Structure

```
youtube-history-tool/
├── watch-history.json       # Your Google Takeout data (optional)
├── client_secrets.json      # Google Cloud credentials (for API mode)
├── token.json               # Saved OAuth tokens (auto-generated)
├── README.md
├── pyproject.toml
├── .gitignore
└── src/
    └── youtube_history_tool/
        ├── __init__.py
        ├── main.py             # Main application logic
        ├── config.py           # Configuration settings
        ├── auth.py             # YouTube API authentication
        ├── history.py          # API-based history retrieval
        └── takeout.py          # Google Takeout data processing
```

## Status

✅ **Ready for Production Use**

- [x] Google Takeout integration with complete watch history
- [x] YouTube API fallback for recent activity
- [x] Interactive search and filtering
- [x] Comprehensive analytics and statistics
- [x] JSON export functionality
- [x] Automatic file detection and smart mode selection
- [x] Robust error handling and user guidance

## Contributing

This tool processes your personal YouTube data locally. No data is transmitted anywhere except for standard YouTube API calls (when using API mode).

## Security Notes

- **All processing happens locally** on your machine
- `client_secrets.json`, `watch_history.json` and `token.json` are gitignored
- **Google Takeout data** is processed offline
- **API credentials** are only used for direct YouTube API communication
- **Revoke access** anytime in your Google Account settings

## Next Steps

- **Advanced filtering** (date ranges, channel filtering, duration filters)
- **Data visualization** (viewing patterns, time-based charts)
- **Export formats** (CSV, Excel, database integration)
- **Playlist analysis** and recommendation features
