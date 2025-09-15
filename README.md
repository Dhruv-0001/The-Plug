# The Plug - AI Video Analyzer

A modern, billion-dollar quality video analysis platform built with Next.js, FastAPI, and Google's Gemini AI. Analyze videos with AI-powered insights and chat with your content.

## 🚀 Features

- **Modern UI/UX** - Cursor-inspired design with smooth animations and professional aesthetics
- **Video Upload** - Drag & drop file upload or paste URLs from YouTube, Instagram, TikTok, X
- **AI Analysis** - Powered by Google Gemini 2.0 Flash with multimodal capabilities
- **Interactive Chat** - Ask questions about your videos and get intelligent responses
- **Real-time Processing** - Live progress indicators and status updates
- **Responsive Design** - Works perfectly on all devices
- **FastAPI Backend** - High-performance API with automatic video processing

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Radix UI** - Accessible components
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - High-performance Python web framework
- **Google Gemini AI** - Multimodal video analysis
- **Phi Agent Framework** - AI orchestration
- **yt-dlp** - Video downloading from various platforms
- **DuckDuckGo Search** - Web search capabilities

## 📋 Prerequisites

- Node.js 18+
- Python 3.11+
- Google AI API Key (for Gemini)
- FFmpeg (for video processing)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd video-llm-analyzer-next

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Environment Setup

Create a `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
ENVIRONMENT=development
DEBUG=True
```

### 3. Start the Backend

```bash
cd backend
python app/main.py
```

The API will be available at `http://localhost:8000`

### 4. Start the Frontend

```bash
# In a new terminal, from the project root
npm run dev
```

The application will be available at `http://localhost:3000`

## 🎯 Usage

### Video Upload Methods

1. **File Upload**
   - Drag and drop video files or click to browse
   - Supports MP4, MOV, AVI formats up to 500MB
   - Real-time progress tracking

2. **URL Upload**
   - Paste URLs from supported platforms:
     - YouTube
     - Instagram
     - TikTok
     - X (Twitter)

### AI Chat Interface

- Ask questions about video content
- Get detailed analysis and insights
- Real-time responses powered by Gemini AI
- Conversation history preservation

## 🏗️ Project Structure

```
video-llm-analyzer-next/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   └── video-analyzer.tsx  # Main application component
│   └── lib/
│       ├── api.ts              # API client
│       └── utils.ts            # Utility functions
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   └── config.py           # Configuration
│   └── requirements.txt        # Python dependencies
└── public/                     # Static assets
```

## 🔧 API Endpoints

### Video Operations
- `POST /upload/video` - Upload video file
- `POST /upload/url` - Upload video from URL
- `POST /chat` - Chat with video
- `DELETE /video/{video_id}` - Delete video

### System
- `GET /` - Health check

## 🎨 Design System

The application uses a modern design system inspired by Cursor:

- **Colors**: Professional dark theme with accent colors
- **Typography**: Geist Sans font family
- **Components**: Accessible, animated UI components
- **Layout**: Clean, minimal design with proper spacing
- **Animations**: Smooth transitions using Framer Motion

## 🚀 Deployment

### Frontend (Vercel)
```bash
npm run build
npm run start
```

### Backend (Railway/DigitalOcean)
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for multimodal capabilities
- Phi Agent Framework for AI orchestration
- yt-dlp for video downloading
- Next.js and FastAPI communities

## 📞 Support

For questions or support, please open an issue on GitHub or contact the development team.

---

**The Plug** - Transforming video analysis with AI-powered insights.
