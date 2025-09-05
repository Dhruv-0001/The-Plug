import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai
import time
from pathlib import Path
import tempfile
from dotenv import load_dotenv
import os
import yt_dlp
import re

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="The Plug",
    page_icon="📹"
)

st.title("The Plug")

@st.cache_resource
def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

def download_video(url):
    """Download video from URL using yt-dlp"""
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video.close()  # Close the file handle so yt-dlp can write to it

    ydl_opts = {
        'outtmpl': temp_video.name,
        'format': 'best[ext=mp4]/best',
        'quiet': False,  # Changed to False to see download progress
        'no_warnings': False,  # Changed to False to see warnings
        'nooverwrites': False,  # Ensure we don't skip downloads due to cache
        # Anti-bot measures
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.youtube.com/',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # Retry and timeout settings
        'retries': 3,
        'fragment_retries': 3,
        'retry_sleep_functions': {
            'http': lambda n: min(60, 2 ** n),
            'fragment': lambda n: min(60, 2 ** n),
        },
        'extractor_retries': 3,
        'socket_timeout': 30,
        # Additional options to avoid detection
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'sleep_interval': 1,
        'max_sleep_interval': 5,
    }

    # Try different download strategies
    download_strategies = [
        ydl_opts,  # Default configuration
        {**ydl_opts, 'format': '18/22/37/38', 'extract_flat': False},  # Specific format codes
        {**ydl_opts, 'cookiesfrombrowser': None, 'ignoreerrors': True},  # Try without cookies
    ]

    last_error = None
    for attempt, strategy in enumerate(download_strategies):
        try:
            st.info(f"Download attempt {attempt + 1}/3...")
            with yt_dlp.YoutubeDL(strategy) as ydl:
                ydl.download([url])

            # Verify the file was downloaded and has content
            if os.path.exists(temp_video.name) and os.path.getsize(temp_video.name) > 0:
                st.success(f"Download successful on attempt {attempt + 1}")
                return temp_video.name
            else:
                raise Exception("Downloaded file is empty or doesn't exist")

        except Exception as e:
            last_error = e
            st.warning(f"Attempt {attempt + 1} failed: {str(e)}")

            # Clean up failed download
            if os.path.exists(temp_video.name):
                try:
                    os.unlink(temp_video.name)
                except:
                    pass

            # Don't retry on the last attempt
            if attempt < len(download_strategies) - 1:
                # Wait before retrying with increasing delay
                wait_time = min(30, 5 * (attempt + 1))
                st.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            continue

    # All attempts failed
    raise Exception(f"All download attempts failed. Last error: {str(last_error)}")

def is_valid_url(url):
    """Check if URL is from supported platforms"""
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)',
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)',
        r'(https?://)?(www\.)?(tiktok\.com)',
        r'(https?://)?(www\.)?(twitter\.com|x\.com)',
    ]
    
    for pattern in patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

# Initialize the agent
multimodal_Agent = initialize_agent()

# Initialize session state for video caching and page navigation
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'current_video_url' not in st.session_state:
    st.session_state.current_video_url = None
if 'current_video_file' not in st.session_state:
    st.session_state.current_video_file = None
if 'last_input_method' not in st.session_state:
    st.session_state.last_input_method = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "upload"  # "upload" or "chat"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def cleanup_video_cache():
    """Clean up cached video file and reset session"""
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        Path(st.session_state.video_path).unlink(missing_ok=True)
        st.session_state.video_path = None
        st.session_state.current_video_url = None
        st.session_state.current_video_file = None
        st.session_state.current_page = "upload"
        st.session_state.chat_history = []

# Page routing based on current state
if st.session_state.current_page == "upload":
    # UPLOAD PAGE
    st.subheader("Upload Your Video")

    # Input method selection
    input_method = st.radio(
        "Choose how to provide your video:",
        ["Upload Video File", "Paste Video Link"],
        help="Select how you want to provide the video for analysis"
    )

    # Clean up cache if user switches input methods
    if st.session_state.last_input_method != input_method:
        cleanup_video_cache()
        st.session_state.last_input_method = input_method

    video_path = None

    if input_method == "Upload Video File":
        # File uploader
        video_file = st.file_uploader(
            "Upload a video file",
            type=['mp4', 'mov', 'avi'],
            help="Upload a video for AI analysis"
        )

        if video_file:
            # Check if this is a different file than the cached one
            if (st.session_state.current_video_file != video_file.name or
                st.session_state.video_path is None or
                not os.path.exists(st.session_state.video_path)):

                # Clean up previous video if it exists
                if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                    Path(st.session_state.video_path).unlink(missing_ok=True)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(video_file.read())
                    st.session_state.video_path = temp_video.name
                    st.session_state.current_video_file = video_file.name
                    st.session_state.current_video_url = None  # Reset URL cache

            video_path = st.session_state.video_path

    else:  # Paste Video Link
        # URL input
        video_url = st.text_input(
            "Paste video link",
            placeholder="https://youtube.com/watch?v=... or Instagram/TikTok/X link",
            help="Paste a video URL from YouTube, Instagram, TikTok, or X"
        )

        if video_url:
            if is_valid_url(video_url):
                # Check if this is a different URL than the cached one
                if (st.session_state.current_video_url != video_url or
                    st.session_state.video_path is None or
                    not os.path.exists(st.session_state.video_path)):

                    # Clean up previous video if it exists
                    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                        Path(st.session_state.video_path).unlink(missing_ok=True)

                    try:
                        with st.spinner("Downloading video..."):
                            st.session_state.video_path = download_video(video_url)
                            st.session_state.current_video_url = video_url
                            st.session_state.current_video_file = None  # Reset file cache
                    except Exception as e:
                        st.error(f"Error downloading video: {e}")
                        st.session_state.video_path = None
                        st.session_state.current_video_url = None

                video_path = st.session_state.video_path
            else:
                st.warning("Please enter a valid YouTube, Instagram, TikTok, or X video URL")

    # Proceed to chat if video is loaded
    if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        if st.button("Start Chat", type="primary", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

elif st.session_state.current_page == "chat":
    # CHAT PAGE
    video_path = st.session_state.video_path

    if not video_path or not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        st.error("Video not found. Please upload a video first.")
        if st.button("Back to Upload"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        # Navigation and controls
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Chat with Your Video")
        with col2:
            if st.button("New Video", help="Upload a different video"):
                cleanup_video_cache()
                st.session_state.current_page = "upload"
                st.rerun()

        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Chat History")
            for i, (query, response) in enumerate(st.session_state.chat_history):
                with st.container():
                    st.markdown(f"**You:** {query}")
                    st.markdown(f"**AI:** {response}")
                    st.divider()

        # Chat input
        st.markdown("### Ask a Question")
        user_query = st.text_input(
            "What would you like to know about this video?",
            placeholder="Example: What is the main topic? Summarize the key points...",
            help="Ask any question about the video content.",
            key="chat_input"
        )

        if st.button("Send", type="primary", use_container_width=True):
            if not user_query.strip():
                st.warning("Please enter a question about the video.")
            else:
                try:
                    with st.spinner("Analyzing video and gathering insights..."):
                        # Upload and process video file
                        processed_video = upload_file(video_path)

                        while processed_video.state.name == "PROCESSING":
                            time.sleep(1)
                            processed_video = get_file(processed_video.name)

                        # Prompt generation for analysis
                        analysis_prompt = (
                            f"""
                            You are an expert video analyst. Analyze the uploaded video and respond to this query:

                            Query: {user_query}

                            Provide a comprehensive, insightful response that includes:
                            1. Direct analysis of the video content
                            2. Key insights and observations
                            3. Any supplementary context that would be helpful
                            4. Actionable takeaways

                            Be conversational and engaging while being thorough and accurate.
                            """
                        )

                        # AI agent processing
                        response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])

                        # Add to chat history
                        st.session_state.chat_history.append((user_query, response.content))

                        # Rerun to update chat history display
                        st.rerun()

                except Exception as error:
                    st.error(f"An error occurred during analysis: {error}")

# Customize UI styling
st.markdown(
    """
    <style>
    .stTextInput input {
        min-height: 40px;
    }
    .stRadio [role="radiogroup"] {
        display: flex;
        gap: 20px;
    }
    .stRadio label {
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)