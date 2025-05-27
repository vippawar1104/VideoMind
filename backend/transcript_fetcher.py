from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import re
import time
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    # Regular expression patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',  # Standard and shortened URLs
        r'youtube\.com\/embed\/([^&\n?]+)',  # Embed URLs
        r'youtube\.com\/v\/([^&\n?]+)'  # Old embed URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_transcript(url, max_retries=3):
    """Fetch transcript for a YouTube video."""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return {
                "success": False,
                "error": "Invalid YouTube URL"
            }
        
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript properly
        formatted_transcript = ""
        for entry in transcript_list:
            formatted_transcript += entry['text'] + " "
        
        return {
            "success": True,
            "transcript": formatted_transcript.strip()
        }
        
    except TranscriptsDisabled:
        return {
            "success": False,
            "error": "Transcripts are disabled for this video"
        }
    except NoTranscriptFound:
        return {
            "success": False,
            "error": "No transcript found for this video"
        }
    except Exception as e:
        if max_retries > 0:
            time.sleep(1)  # Wait before retrying
            return get_transcript(url, max_retries - 1)
        return {
            "success": False,
            "error": f"Failed to fetch transcript after {max_retries} attempts: {str(e)}"
        }
