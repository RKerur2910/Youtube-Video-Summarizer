import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import whisper
from pytube import YouTube
import re

# Load environment variables from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini prompt
prompt = """You are a YouTube video summarizer. Take the transcript text and summarize the entire video,
providing the key points within 250 words. Please provide the summary of the following transcript: """

# Helper: extract video ID robustly
def extract_video_id(url):
    try:
        parsed_url = urlparse(url)
        video_id = parse_qs(parsed_url.query).get('v')
        return video_id[0] if video_id else None
    except Exception:
        return None

# Fetch transcript or fallback to Whisper
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None, "Invalid YouTube link."

        # Try YouTube transcript API
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en'])
            transcript_text = transcript.fetch()
            transcript_full = " ".join([i.text for i in transcript_text])
            print("YouTube transcript preview:", transcript_full[:200])
            return transcript_full, None
        except (TranscriptsDisabled, NoTranscriptFound):
            print("Transcript not found via API. Using Whisper fallback...")

        # Whisper fallback
        yt = YouTube(youtube_video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_path = audio_stream.download(filename="temp_audio.mp4")

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        os.remove(audio_path)

        whisper_transcript = result.get("text", "").strip()
        print("Whisper transcript preview:", whisper_transcript[:200])

        if not whisper_transcript:
            print("Whisper returned empty text.")
            return None, "Whisper failed to transcribe audio."

        return whisper_transcript, None

    except Exception as e:
        print("Transcript extraction failed:", e)
        return None, f"Unexpected error: {e}"

# Generate summary using Gemini
def generate_gemini_content(transcript_text, prompt, max_chars=12000):
    print("ENTERED generate_gemini_content()")
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        print("Gemini model loaded")

        # Clean and check
        import re
        if not transcript_text or not transcript_text.strip():
            raise ValueError("Transcript is empty — nothing to summarize.")

        cleaned_transcript = re.sub(r'[^\x00-\x7F]+', '', transcript_text.strip())
        cleaned_prompt = re.sub(r'[^\x00-\x7F]+', '', prompt.strip())
        combined_input = cleaned_prompt + cleaned_transcript

        if len(combined_input) > max_chars:
            st.warning("Transcript is long — only the beginning will be summarized.")
            combined_input = combined_input[:max_chars]

        print("Input length:", len(combined_input))
        print("Input preview:", combined_input[:200])

        response = model.generate_content(combined_input)
        print("Gemini response received")
        return response.text

    except Exception as e:
        print("Exception in generate_gemini_content():", e)
        st.error(f"Gemini Error: {e}")
        return None


# Streamlit UI
st.set_page_config(page_title="YouTube Notes Generator", layout="centered")
st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    with st.spinner("Fetching transcript and summarizing..."):
        transcript_text, error = extract_transcript_details(youtube_link)
        if error:
            st.error(error)
        elif transcript_text and transcript_text.strip():
            print("Transcript ready for Gemini:", transcript_text[:200])
            try:
                summary = generate_gemini_content(transcript_text, prompt)
                if summary:
                    st.markdown("## 📄 Detailed Notes")
                    st.write(summary)
            except Exception as e:
                st.error(f"Error generating summary: {e}")
        else:
            st.error("Transcript is empty — Gemini cannot summarize nothing.")
