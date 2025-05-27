import streamlit as st
import sys
import os
import plotly.express as px
import pandas as pd
from datetime import datetime
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import time

# Try importing plotly, but don't fail if it's not available
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly is not available. Some visualization features will be disabled.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    st.warning("Pandas is not available. Some data processing features will be disabled.")

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.transcript_fetcher import get_transcript
from backend.summarizer import generate_summary, generate_key_points
from backend.question_suggester import generate_questions, suggest_resources

# Set page config
st.set_page_config(
    page_title="VideoMind - YouTube Content Analyzer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        /* Main content styling */
        .main {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Title styling with neon glow */
        .title-text {
            font-size: 3.5rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #00ff00, #00ffff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5),
                         0 0 20px rgba(0, 255, 0, 0.3),
                         0 0 30px rgba(0, 255, 0, 0.2);
            animation: neonPulse 2s ease-in-out infinite;
        }
        
        /* Subtitle styling with neon glow */
        .subtitle-text {
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 2rem;
            color: #ffffff;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.5),
                         0 0 20px rgba(255, 255, 255, 0.3);
        }
        
        /* Button styling with neon glow */
        .stButton>button {
            background: linear-gradient(45deg, #00ff00, #00ffff);
            color: #ffffff;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3),
                       0 0 20px rgba(0, 255, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5),
                       0 0 30px rgba(0, 255, 0, 0.3);
        }
        
        /* Text input styling */
        .stTextInput>div>div>input {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            border-radius: 10px;
            padding: 0.5rem 1rem;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
        }
        
        /* Neon pulse animation */
        @keyframes neonPulse {
            0% {
                text-shadow: 0 0 10px rgba(0, 255, 0, 0.5),
                            0 0 20px rgba(0, 255, 0, 0.3),
                            0 0 30px rgba(0, 255, 0, 0.2);
            }
            50% {
                text-shadow: 0 0 15px rgba(0, 255, 0, 0.7),
                            0 0 25px rgba(0, 255, 0, 0.5),
                            0 0 35px rgba(0, 255, 0, 0.3);
            }
            100% {
                text-shadow: 0 0 10px rgba(0, 255, 0, 0.5),
                            0 0 20px rgba(0, 255, 0, 0.3),
                            0 0 30px rgba(0, 255, 0, 0.2);
            }
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem;">
        <div style="background: rgba(0, 255, 0, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 1rem 3rem; border-radius: 20px; border: 1px solid rgba(0, 255, 0, 0.2); box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);">
            <h1 class="title-text">VideoMind</h1>
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Transform YouTube videos into structured learning experiences</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### About VideoMind")
    st.markdown("""
    VideoMind is an AI-powered tool that helps you:
    - 📝 Generate concise summaries
    - 🔑 Extract key points
    - ❓ Create follow-up questions
    - 📚 Suggest learning resources
    
    Simply paste a YouTube URL to get started!
    """)
    
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
    1. Paste a YouTube video URL
    2. Click 'Analyze Video'
    3. Wait for the analysis
    4. Explore the results!
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # URL input with improved styling
    video_url = st.text_input(
        "Enter YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste a YouTube video URL to analyze its content"
    )

with col2:
    st.markdown("### ")
    analyze_button = st.button("🎥 Analyze Video", use_container_width=True)

if analyze_button and video_url:
    try:
        with st.spinner("Fetching video transcript..."):
            transcript_result = get_transcript(video_url)
            
        if transcript_result.get("success"):
            transcript = transcript_result.get("transcript")
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🔑 Key Points", "❓ Questions", "📚 Resources"])
            
            with tab1:
                with st.spinner("Generating summary..."):
                    summary_result = generate_summary(transcript)
                    if summary_result.get("success"):
                        st.markdown("### Video Summary")
                        st.markdown(summary_result.get("summary"))
                    else:
                        st.error(summary_result.get("error"))
            
            with tab2:
                with st.spinner("Extracting key points..."):
                    key_points_result = generate_key_points(transcript)
                    if key_points_result.get("success"):
                        st.markdown("### Key Points")
                        st.markdown(key_points_result.get("key_points"))
                    else:
                        st.error(key_points_result.get("error"))
            
            with tab3:
                with st.spinner("Generating questions..."):
                    questions_result = generate_questions(transcript)
                    if questions_result.get("success"):
                        st.markdown("### Follow-up Questions")
                        for i, question in enumerate(questions_result.get("questions"), 1):
                            st.markdown(f"{i}. {question}")
                    else:
                        st.error(questions_result.get("error"))
            
            with tab4:
                with st.spinner("Suggesting resources..."):
                    resources_result = suggest_resources(transcript)
                    if resources_result.get("success"):
                        st.markdown("### Learning Resources")
                        for i, resource in enumerate(resources_result.get("resources"), 1):
                            st.markdown(f"{i}. {resource}")
                    else:
                        st.error(resources_result.get("error"))
        else:
            st.error(transcript_result.get("error"))
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    # Show placeholder content when no video is being analyzed
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: rgba(30, 41, 59, 0.7); border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.1); backdrop-filter: blur(10px);'>
        <h2 style='color: #60a5fa; font-size: 2rem; margin-bottom: 1rem;'>Welcome to VideoMind! 🎥</h2>
        <p style='color: #94a3b8; font-size: 1.1rem; opacity: 0.8;'>Paste a YouTube URL above to start analyzing video content.</p>
    </div>
    """, unsafe_allow_html=True)
