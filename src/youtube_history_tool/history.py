"""
YouTube watch history retrieval and management
"""

from datetime import datetime
from typing import List, Dict, Optional
import json

from .config import DEFAULT_MAX_RESULTS


class WatchHistoryItem:
    """Represents a single item from YouTube watch history"""

    def __init__(self, data: Dict):
        self.raw_data = data

        # Parse the activity data
        snippet = data.get('snippet', {})
        content_details = data.get('contentDetails', {})

        self.title = snippet.get('title', 'Unknown Title')
        self.published_at = snippet.get('publishedAt', '')
        self.channel_title = snippet.get('channelTitle', 'Unknown Channel')
        self.description = snippet.get('description', '')
        self.activity_type = snippet.get('type', '')

        # Try to get video ID from different possible locations
        self.video_id = None
        if 'upload' in content_details:
            self.video_id = content_details['upload'].get('videoId')
        elif 'playlistItem' in content_details:
            resource_id = content_details['playlistItem'].get('resourceId', {})
            self.video_id = resource_id.get('videoId')

        self.video_url = f"https://www.youtube.com/watch?v={self.video_id}" if self.video_id else None

        # Parse timestamp
        self.timestamp = self._parse_timestamp(self.published_at)

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse YouTube timestamp to datetime object"""
        if not timestamp_str:
            return None
        try:
            # YouTube uses ISO 8601 format
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def to_dict(self) -> Dict:
        """Convert to dictionary for export/serialization"""
        return {
            'title': self.title,
            'channel': self.channel_title,
            'video_id': self.video_id,
            'video_url': self.video_url,
            'published_at': self.published_at,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'activity_type': self.activity_type,
            'description': self.description[:200] + '...' if len(self.description) > 200 else self.description
        }

    def __str__(self) -> str:
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M') if self.timestamp else 'Unknown date'
        return f"[{timestamp_str}] {self.title} - {self.channel_title}"

    def __repr__(self) -> str:
        return f"WatchHistoryItem(title='{self.title}', channel='{self.channel_title}')"


class HistoryRetriever:
    """Retrieves and manages YouTube watch history"""

    def __init__(self, youtube_service):
        self.youtube = youtube_service
        self._cache = []

    def get_watch_history(self, max_results: int = DEFAULT_MAX_RESULTS) -> List[WatchHistoryItem]:
        """
        Retrieve watch history from YouTube API

        Note: YouTube's API has limited access to watch history due to privacy policies.
        This method retrieves what's available through the activities endpoint.
        """
        try:
            print(f"📡 Fetching up to {max_results} items from YouTube API...")

            # Get activities (this includes various user activities, not just watch history)
            request = self.youtube.activities().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=min(max_results, 50)  # API limit is 50 per request
            )

            response = request.execute()
            items = response.get('items', [])

            print(f"📥 Retrieved {len(items)} activity items from API")

            # Filter and convert to WatchHistoryItem objects
            history_items = []
            for item in items:
                # We're interested in uploads and playlist items that might represent watched videos
                activity_type = item['snippet'].get('type', '')
                if activity_type in ['upload', 'playlistItem', 'recommendation']:
                    try:
                        history_item = WatchHistoryItem(item)
                        if history_item.video_id:  # Only include items with valid video IDs
                            history_items.append(history_item)
                    except Exception as e:
                        print(f"⚠️  Warning: Could not parse activity item: {e}")
                        continue

            print(f"✅ Processed {len(history_items)} valid history items")

            # Cache the results
            self._cache = history_items
            return history_items

        except Exception as e:
            print(f"❌ Error retrieving watch history: {e}")
            print("This might be due to:")
            print("  - YouTube API limitations on watch history access")
            print("  - Privacy settings on your Google account")
            print("  - API quota limits")
            return []

    def search_history(self, query: str, history: Optional[List[WatchHistoryItem]] = None) -> List[WatchHistoryItem]:
        """
        Search through watch history for specific terms
        """
        if history is None:
            history = self._cache

        if not history:
            print("⚠️  No history data to search. Try retrieving history first.")
            return []

        query_lower = query.lower()
        matching_items = []

        for item in history:
            # Search in title, channel name, and description
            if (query_lower in item.title.lower() or
                    query_lower in item.channel_title.lower() or
                    query_lower in item.description.lower()):
                matching_items.append(item)

        return matching_items

    def export_to_json(self, history: List[WatchHistoryItem], filename: str = "watch_history.json"):
        """Export history to JSON file"""
        try:
            data = [item.to_dict() for item in history]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Exported {len(history)} items to {filename}")
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")

    def print_summary(self, history: List[WatchHistoryItem]):
        """Print a summary of the watch history"""
        if not history:
            print("📊 No history items to summarize")
            return

        print(f"\n📊 Watch History Summary")
        print(f"{'=' * 50}")
        print(f"Total items: {len(history)}")

        # Count by channel
        channels = {}
        for item in history:
            channels[item.channel_title] = channels.get(item.channel_title, 0) + 1

        print(f"Unique channels: {len(channels)}")

        # Show top channels
        if channels:
            print(f"\nTop channels:")
            sorted_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)
            for channel, count in sorted_channels[:5]:
                print(f"  {channel}: {count} videos")

        # Show date range
        timestamps = [item.timestamp for item in history if item.timestamp]
        if timestamps:
            oldest = min(timestamps)
            newest = max(timestamps)
            print(f"\nDate range: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
