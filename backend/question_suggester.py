import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use a different model for question generation
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}",
    "Content-Type": "application/json"
}

def generate_questions(transcript):
    """Generate follow-up questions based on the video transcript."""
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
        questions = []
        
        for chunk in chunks:
            prompt = f"Generate 3 thought-provoking questions about this text: {chunk}"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "min_length": 50,
                    "do_sample": True,
                    "temperature": 0.7
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
                    generated_text = response.json()[0]["summary_text"]
                    # Split the generated text into questions
                    chunk_questions = [q.strip() for q in generated_text.split('?') if q.strip()]
                    questions.extend(chunk_questions)
                    break
                
                if attempt == max_retries - 1:
                    # If all retries failed, use extractive questions
                    sentences = chunk.split('.')
                    important_sentences = [s.strip() for s in sentences if len(s.split()) > 5]
                    for sentence in important_sentences[:3]:
                        question = f"What are the implications of {sentence.lower()}?"
                        questions.append(question)
        
        # Ensure we have at least 5 questions
        while len(questions) < 5:
            questions.append("How does this content relate to current trends in the field?")
        
        return {
            "success": True,
            "questions": questions[:5]  # Return top 5 questions
        }
    except Exception as e:
        raise Exception(f"Error generating questions: {str(e)}")

def suggest_resources(transcript):
    """Suggest additional learning resources related to the video content."""
    try:
        # Extract key topics from the transcript
        words = transcript.lower().split()
        common_words = set(['the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'that', 'with', 'on', 'at'])
        topics = [word for word in words if word not in common_words and len(word) > 3]
        
        # Generate resource suggestions based on topics
        resources = []
        for topic in topics[:3]:
            resources.extend([
                f"Online course: Introduction to {topic.title()}",
                f"Book: The Complete Guide to {topic.title()}",
                f"Website: {topic.title()}.org - A comprehensive resource"
            ])
        
        # Ensure we have at least 5 resources
        while len(resources) < 5:
            resources.append("YouTube channel: Educational content on this topic")
        
        return {
            "success": True,
            "resources": resources[:5]  # Return top 5 resources
        }
    except Exception as e:
        raise Exception(f"Error suggesting resources: {str(e)}")
