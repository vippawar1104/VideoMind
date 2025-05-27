import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use a different model for summarization
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
    "Content-Type": "application/json"
}

def generate_summary(transcript):
    """Generate a summary of the video transcript."""
    if not os.getenv('HUGGINGFACE_API_KEY'):
        raise ValueError("""
        Hugging Face API key not found! Please follow these steps:
        1. Create a .env file in the project root directory
        2. Add your Hugging Face API key like this: HUGGINGFACE_API_KEY=your-api-key-here
        3. Get your API key from: https://huggingface.co/settings/tokens
        """)
    
    try:
        # Split transcript into chunks of 1000 characters
        chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 1000)]
        summaries = []
        
        for chunk in chunks:
            payload = {
                "inputs": chunk,
                "parameters": {
                    "max_length": 150,
                    "min_length": 50,
                    "do_sample": False,
                    "truncation": True
                }
            }
            
            max_retries = 3
            for attempt in range(max_retries):
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    import time
                    time.sleep(20)
                    continue
                
                if response.status_code == 200:
                    summaries.append(response.json()[0]["summary_text"])
                    break
                
                if attempt == max_retries - 1:
                    # If all retries failed, use extractive summary
                    sentences = chunk.split('.')
                    summary = '. '.join(sentences[:3]) + '.'
                    summaries.append(summary)
        
        return {
            "success": True,
            "summary": " ".join(summaries)
        }
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def generate_key_points(transcript):
    """Extract key points from the video transcript."""
    try:
        # Split transcript into chunks of 1000 characters
        chunks = [transcript[i:i+1000] for i in range(0, len(transcript), 1000)]
        key_points = []
        
        for chunk in chunks:
            # Simple extractive key points
            sentences = chunk.split('.')
            important_sentences = [s.strip() for s in sentences if len(s.split()) > 5]
            key_points.extend(important_sentences[:3])
        
        # Format key points
        formatted_points = []
        for i, point in enumerate(key_points[:5], 1):
            formatted_points.append(f"{i}. {point.strip()}")
        
        return {
            "success": True,
            "key_points": "\n".join(formatted_points)
        }
    except Exception as e:
        raise Exception(f"Error generating key points: {str(e)}")