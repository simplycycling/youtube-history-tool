# YouTube Watch History Tool

A Python script to search through your YouTube watch history programmatically.

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

## Development

- Run script: uv run python -m youtube_history_tool.main
- Run with development mode: uv run --dev python -m youtube_history_tool.main
- Install new dependency: uv add <package-name>
- Format code: uv run black .
- Lint: uv run ruff check .

Status
🚧 Work in Progress 🚧

- [x] Basic project structure with uv  
- [ ] Google OAuth setup  
- [ ] API integration  
- [ ] Search functionality  
