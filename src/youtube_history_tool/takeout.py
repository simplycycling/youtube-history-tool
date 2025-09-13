"""
Google Takeout data processing for YouTube watch history
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse

from .history import WatchHistoryItem


class TakeoutWatchHistoryItem:
    """Represents a watch history item from Google Takeout data"""

    def __init__(self, data: Dict):
        self.raw_data = data

        # Parse Takeout data structure
        self.title = data.get('title', 'Unknown Title')
        # Remove "Watched " prefix if present
        if self.title.startswith('Watched '):
            self.title = self.title[8:]

        self.title_url = data.get('titleUrl', '')
        self.subtitles = data.get('subtitles', [])
        self.time = data.get('time', '')

        # Extract video ID from URL
        self.video_id = self._extract_video_id(self.title_url)
        self.video_url = f"https://www.youtube.com/watch?v={self.video_id}" if self.video_id else self.title_url

        # Extract channel name from subtitles
        self.channel_title = self._extract_channel_name()

        # Parse timestamp
        self.timestamp = self._parse_timestamp(self.time)

        # Additional fields for compatibility
        self.description = ''
        self.activity_type = 'watch'
        self.published_at = self.time

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        if not url:
            return None

        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Try parsing query parameters
        try:
            parsed_url = urlparse(url)
            if 'v' in parse_qs(parsed_url.query):
                return parse_qs(parsed_url.query)['v'][0]
        except:
            pass

        return None

    def _extract_channel_name(self) -> str:
        """Extract channel name from subtitles"""
        for subtitle in self.subtitles:
            if isinstance(subtitle, dict):
                name = subtitle.get('name', '')
                if name:
                    return name
            elif isinstance(subtitle, str):
                return subtitle
        return 'Unknown Channel'

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse Google Takeout timestamp"""
        if not timestamp_str:
            return None
        try:
            # Google Takeout format: "Dec 15, 2023, 3:45:23 PM PST"
            # Remove timezone info for basic parsing
            clean_time = re.sub(r'\s+[A-Z]{3,4}$', '', timestamp_str)

            # Try different formats
            formats = [
                "%b %d, %Y, %I:%M:%S %p",  # Dec 15, 2023, 3:45:23 PM
                "%b %d, %Y, %H:%M:%S",  # Dec 15, 2023, 15:45:23
                "%Y-%m-%d %H:%M:%S",  # 2023-12-15 15:45:23
                "%Y-%m-%dT%H:%M:%S",  # 2023-12-15T15:45:23
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(clean_time, fmt)
                except ValueError:
                    continue

            # If all else fails, try parsing just the date
            date_match = re.search(r'(\w{3}\s+\d{1,2},\s+\d{4})', timestamp_str)
            if date_match:
                return datetime.strptime(date_match.group(1), "%b %d, %Y")

        except Exception as e:
            print(f"Warning: Could not parse timestamp '{timestamp_str}': {e}")

        return None

    def to_dict(self) -> Dict:
        """Convert to dictionary for export/serialization"""
        return {
            'title': self.title,
            'channel': self.channel_title,
            'video_id': self.video_id,
            'video_url': self.video_url,
            'watched_at': self.time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'activity_type': self.activity_type,
            'description': self.description
        }

    def __str__(self) -> str:
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else 'Unknown date'
        return f"[{timestamp_str}] {self.title} - {self.channel_title}"

    def __repr__(self) -> str:
        return f"TakeoutWatchHistoryItem(title='{self.title}', channel='{self.channel_title}')"


class TakeoutProcessor:
    """Processes Google Takeout YouTube data"""

    def __init__(self):
        self._cache = []

    def load_watch_history(self, file_path: Union[str, Path]) -> List[TakeoutWatchHistoryItem]:
        """
        Load watch history from Google Takeout JSON file

        Args:
            file_path: Path to watch-history.json from Google Takeout

        Returns:
            List of TakeoutWatchHistoryItem objects
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Takeout file not found: {file_path}")

        print(f"📂 Loading watch history from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"📥 Loaded {len(data)} raw entries from Takeout")

            # Process each entry
            history_items = []
            skipped = 0

            for entry in data:
                try:
                    # Skip entries without titles or URLs
                    if not entry.get('title') or not entry.get('titleUrl'):
                        skipped += 1
                        continue

                    # Skip non-video entries (like searches, etc.)
                    if 'youtube.com/watch' not in entry.get('titleUrl', ''):
                        skipped += 1
                        continue

                    item = TakeoutWatchHistoryItem(entry)
                    if item.video_id:  # Only include items with valid video IDs
                        history_items.append(item)
                    else:
                        skipped += 1

                except Exception as e:
                    print(f"⚠️  Warning: Could not parse entry: {e}")
                    skipped += 1
                    continue

            print(f"✅ Processed {len(history_items)} valid watch history items")
            if skipped > 0:
                print(f"⚠️  Skipped {skipped} invalid/non-video entries")

            # Sort by timestamp (newest first)
            history_items.sort(key=lambda x: x.timestamp or datetime.min, reverse=True)

            self._cache = history_items
            return history_items

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in takeout file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error processing takeout file: {e}")

    def search_history(self, query: str, history: Optional[List[TakeoutWatchHistoryItem]] = None) -> List[
        TakeoutWatchHistoryItem]:
        """Search through Takeout watch history"""
        if history is None:
            history = self._cache

        if not history:
            print("⚠️  No Takeout history data to search. Try loading a file first.")
            return []

        query_lower = query.lower()
        matching_items = []

        for item in history:
            if (query_lower in item.title.lower() or
                    query_lower in item.channel_title.lower()):
                matching_items.append(item)

        return matching_items

    def get_date_range(self, history: List[TakeoutWatchHistoryItem]) -> tuple:
        """Get the date range of watch history"""
        timestamps = [item.timestamp for item in history if item.timestamp]
        if not timestamps:
            return None, None
        return min(timestamps), max(timestamps)

    def get_top_channels(self, history: List[TakeoutWatchHistoryItem], limit: int = 10) -> List[tuple]:
        """Get top watched channels with counts"""
        channel_counts = {}
        for item in history:
            channel = item.channel_title
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

        return sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def export_to_json(self, history: List[TakeoutWatchHistoryItem], filename: str = "takeout_watch_history.json"):
        """Export Takeout history to JSON file"""
        try:
            data = [item.to_dict() for item in history]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Exported {len(history)} items to {filename}")
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")

    def print_summary(self, history: List[TakeoutWatchHistoryItem]):
        """Print a summary of the Takeout watch history"""
        if not history:
            print("📊 No Takeout history items to summarize")
            return

        print(f"\n📊 Google Takeout Watch History Summary")
        print(f"{'=' * 50}")
        print(f"Total videos watched: {len(history)}")

        # Date range
        start_date, end_date = self.get_date_range(history)
        if start_date and end_date:
            days_span = (end_date - start_date).days
            print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print(f"Time span: {days_span} days")
            if days_span > 0:
                avg_per_day = len(history) / days_span
                print(f"Average videos per day: {avg_per_day:.1f}")

        # Top channels
        top_channels = self.get_top_channels(history, limit=10)
        if top_channels:
            print(f"\nTop 10 watched channels:")
            for i, (channel, count) in enumerate(top_channels, 1):
                percentage = (count / len(history)) * 100
                print(f"  {i:2d}. {channel}: {count} videos ({percentage:.1f}%)")


def find_takeout_files(directory: Union[str, Path] = ".") -> List[Path]:
    """
    Find potential Google Takeout watch history files in a directory

    Args:
        directory: Directory to search in (default: current directory)

    Returns:
        List of potential watch history JSON files
    """
    directory = Path(directory)

    # Common patterns for Takeout watch history files
    patterns = [
        "**/watch-history.json",
        "**/Watch History.json",
        "**/Takeout/YouTube*/history/watch-history.json",
        "**/YouTube*/watch-history.json",
        "**/*watch*history*.json"
    ]

    found_files = []
    for pattern in patterns:
        found_files.extend(directory.glob(pattern))

    # Remove duplicates and return
    return list(set(found_files))