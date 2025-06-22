# Youtube-Video-Summarizer

This project is a Streamlit web application that summarizes the content of any public YouTube video using large language models. It extracts the transcript from the video and generates a concise summary using Google’s Gemini 1.5 Pro model. If captions are not available, the application transcribes the video using Whisper, ensuring it can handle nearly any video input.

## Project Overview

The goal of this project is to automate the process of understanding long-form video content by generating accurate, structured summaries from YouTube videos. It combines video processing, transcription, and language modeling into an end-to-end summarization tool.

### How It Works

1. The user provides a YouTube video link through the web interface.
2. The app tries to fetch the video transcript using the YouTubeTranscriptAPI.
3. If captions are not available, the app downloads the video’s audio and transcribes it using Whisper.
4. The transcript is cleaned and processed, then sent to the Gemini 1.5 Pro model for summarization.
5. The final summary is displayed in the Streamlit interface.

## Features

- Captures transcript using YouTubeTranscriptAPI
- Automatically uses Whisper as fallback for audio-based transcription
- Summarizes text using Gemini 1.5 Pro from Google Generative AI
- Displays video thumbnail, summary, and error feedback in a simple interface
- Supports all public YouTube videos with English audio

## Tech Stack

- Python
- Streamlit
- Google Generative AI (Gemini)
- OpenAI Whisper
- YouTubeTranscriptAPI
- Pytube
- dotenv
- ffmpeg
