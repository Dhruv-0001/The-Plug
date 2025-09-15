import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai
import time
from pathlib import Path
import tempfile
import os
import requests
import re
from urllib.parse import urlparse
import hashlib

# Load environment variables from Streamlit secrets
if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="The Plug",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
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

def get_video_info(url):
    """Get video information without downloading - for cloud compatibility"""
    try:
        # Use yt-dlp to get video info only (no download)
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,  # Don't download, just get info
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        return {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'description': info.get('description', ''),
            'thumbnail': info.get('thumbnail', ''),
            'formats': info.get('formats', [])
        }
    except Exception as e:
        st.error(f"Could not extract video information: {e}")
        return None

def download_small_video_segment(url, max_size_mb=50):
    """Download a small segment of video for analysis - Streamlit Cloud compatible"""
    try:
        import yt_dlp
        
        # Create a temporary file
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.close()
        
        # Conservative download options for cloud environment
        ydl_opts = {
            'outtmpl': temp_video.name,
            'format': f'best[filesize<{max_size_mb}M]/worst',  # Prefer smaller files
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 1,  # Reduced retries for cloud
            'fragment_retries': 1,
            'extractaudio': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Check if file exists and has content
        if os.path.exists(temp_video.name) and os.path.getsize(temp_video.name) > 0:
            file_size_mb = os.path.getsize(temp_video.name) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                os.unlink(temp_video.name)
                raise Exception(f"Video too large ({file_size_mb:.1f}MB). Please use a smaller video or upload directly.")
            return temp_video.name
        else:
            raise Exception("Downloaded file is empty or doesn't exist")
            
    except Exception as e:
        # Clean up on failure
        if os.path.exists(temp_video.name):
            try:
                os.unlink(temp_video.name)
            except:
                pass
        raise e

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

def display_video_info(info):
    """Display video information in a nice format"""
    if not info:
        return
        
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if info.get('thumbnail'):
            st.image(info['thumbnail'], width=200)
    
    with col2:
        st.subheader(info.get('title', 'Unknown Title'))
        st.write(f"**Uploader:** {info.get('uploader', 'Unknown')}")
        
        duration = info.get('duration', 0)
        if duration:
            minutes, seconds = divmod(duration, 60)
            st.write(f"**Duration:** {int(minutes)}:{int(seconds):02d}")
        
        if info.get('description'):
            with st.expander("Description"):
                st.write(info['description'][:500] + "..." if len(info['description']) > 500 else info['description'])

# Initialize the agent
multimodal_Agent = initialize_agent()

# Initialize session state
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'current_video_url' not in st.session_state:
    st.session_state.current_video_url = None
if 'current_video_file' not in st.session_state:
    st.session_state.current_video_file = None
if 'last_input_method' not in st.session_state:
    st.session_state.last_input_method = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "upload"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'video_info' not in st.session_state:
    st.session_state.video_info = None

def cleanup_video_cache():
    """Clean up cached video file and reset session"""
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        Path(st.session_state.video_path).unlink(missing_ok=True)
        st.session_state.video_path = None
        st.session_state.current_video_url = None
        st.session_state.current_video_file = None
        st.session_state.current_page = "upload"
        st.session_state.chat_history = []
        st.session_state.video_info = None

# Check if we're running in Streamlit Cloud
is_cloud_deployment = 'streamlit.io' in st.get_option('server.baseUrlPath') if hasattr(st, 'get_option') else False

# Page routing
if st.session_state.current_page == "upload":
    # UPLOAD PAGE
    st.subheader("Upload Your Video")
    
    # Show cloud deployment notice
    if is_cloud_deployment:
        st.info("🌥️ **Cloud Deployment Notice**: For optimal performance, please use smaller videos (<50MB) or upload files directly when using URL downloads.")

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
        # File uploader with size limits for cloud
        max_size = 200 if is_cloud_deployment else 500
        video_file = st.file_uploader(
            f"Upload a video file (max {max_size}MB)",
            type=['mp4', 'mov', 'avi'],
            help=f"Upload a video for AI analysis. Max size: {max_size}MB"
        )

        if video_file:
            # Check file size
            file_size_mb = video_file.size / (1024 * 1024)
            if file_size_mb > max_size:
                st.error(f"File too large ({file_size_mb:.1f}MB). Please upload a file smaller than {max_size}MB.")
            else:
                # Process file upload
                if (st.session_state.current_video_file != video_file.name or
                    st.session_state.video_path is None or
                    not os.path.exists(st.session_state.video_path)):

                    # Clean up previous video
                    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                        Path(st.session_state.video_path).unlink(missing_ok=True)

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                        temp_video.write(video_file.read())
                        st.session_state.video_path = temp_video.name
                        st.session_state.current_video_file = video_file.name
                        st.session_state.current_video_url = None
                        st.session_state.video_info = {'title': video_file.name, 'uploader': 'Uploaded File'}

                video_path = st.session_state.video_path

    else:  # Paste Video Link
        # URL input with enhanced cloud support
        video_url = st.text_input(
            "Paste video link",
            placeholder="https://youtube.com/watch?v=... or Instagram/TikTok/X link",
            help="Paste a video URL. For cloud deployment, shorter videos work better."
        )

        if video_url:
            if is_valid_url(video_url):
                # Show video info first
                if st.session_state.current_video_url != video_url:
                    with st.spinner("Getting video information..."):
                        video_info = get_video_info(video_url)
                        st.session_state.video_info = video_info
                
                # Display video information
                if st.session_state.video_info:
                    display_video_info(st.session_state.video_info)
                    
                    # Warning for long videos in cloud
                    duration = st.session_state.video_info.get('duration', 0)
                    if is_cloud_deployment and duration > 600:  # 10 minutes
                        st.warning("⚠️ This video is quite long. Download might be slow or fail in cloud environment. Consider using a shorter video or uploading the file directly.")
                
                # Download button
                if st.button("Download and Process Video", type="secondary"):
                    # Check if different URL
                    if (st.session_state.current_video_url != video_url or
                        st.session_state.video_path is None or
                        not os.path.exists(st.session_state.video_path)):

                        # Clean up previous video
                        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                            Path(st.session_state.video_path).unlink(missing_ok=True)

                        try:
                            with st.spinner("Downloading video... This may take a moment."):
                                max_size = 50 if is_cloud_deployment else 100
                                st.session_state.video_path = download_small_video_segment(video_url, max_size)
                                st.session_state.current_video_url = video_url
                                st.session_state.current_video_file = None
                                st.success("Video downloaded successfully!")
                        except Exception as e:
                            st.error(f"Error downloading video: {e}")
                            st.info("💡 **Tip**: Try uploading the video file directly instead, or use a shorter/smaller video.")
                            st.session_state.video_path = None
                            st.session_state.current_video_url = None

                video_path = st.session_state.video_path
            else:
                st.warning("Please enter a valid YouTube, Instagram, TikTok, or X video URL")

    # Proceed to chat if video is loaded
    if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        st.success(f"✅ Video ready for analysis ({file_size_mb:.1f}MB)")
        
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
            if st.session_state.video_info:
                st.caption(f"Analyzing: {st.session_state.video_info.get('title', 'Unknown')}")
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
                    st.markdown(f"**The Plug:** {response}")
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

                        # Wait for processing with timeout for cloud
                        timeout_count = 0
                        max_timeout = 120 if is_cloud_deployment else 300  # Shorter timeout for cloud
                        
                        while processed_video.state.name == "PROCESSING":
                            time.sleep(2)
                            timeout_count += 2
                            processed_video = get_file(processed_video.name)
                            
                            if timeout_count > max_timeout:
                                st.error("Video processing is taking too long. Please try with a smaller video.")
                                break

                        if processed_video.state.name == "ACTIVE":
                            # Enhanced prompt for better analysis
                            analysis_prompt = f"""
                            You are an expert video analyzer. Analyze the uploaded video and respond to this query:

                            Query: {user_query}

                            Provide a comprehensive, insightful response that includes:
                            1. Direct analysis of the video content
                            2. Key insights and observations
                            3. Any supplementary context that would be helpful
                            4. Actionable takeaways

                            Be conversational and engaging while being thorough and accurate.
                            Speak casually, humble and naturally. 
                            Keep responses concise but informative.
                            """

                            # AI agent processing
                            response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])

                            # Add to chat history
                            st.session_state.chat_history.append((user_query, response.content))

                            # Rerun to update chat history display
                            st.rerun()
                        else:
                            st.error("Video processing failed. Please try again with a different video.")

                except Exception as error:
                    st.error(f"An error occurred during analysis: {error}")
                    if is_cloud_deployment:
                        st.info("💡 **Cloud Tip**: If you're experiencing issues, try using a smaller video file or upload directly instead of using URLs.")

# Add custom styling
st.markdown("""
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
.stAlert {
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("🚀 **The Plug** - AI-powered video analysis made simple")
if is_cloud_deployment:
    st.caption("Running on Streamlit Cloud ☁️")
