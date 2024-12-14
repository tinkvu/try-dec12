import streamlit as st
import sounddevice as sd
import numpy as np
import wavio
from groq import Groq
from gtts import gTTS
from pydub import AudioSegment
from deepgram import Deepgram, SpeakOptions

# Initialize Groq client
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Deepgram client
DEEPGRAM_API_KEY = "805291bd449136dca714e320d57d53476efdcc13"
deepgram_client = Deepgram(DEEPGRAM_API_KEY)

# Function to record audio
def record_audio(duration=5, filename="recorded_audio.wav"):
    st.write("Recording...")
    fs = 44100  # Sample rate
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished
    wavio.write(filename, audio, fs, sampwidth=2)  # Save as WAV file
    st.success(f"Recording complete. Saved as {filename}.")
    return filename

# Function to transcribe audio using Groq Whisper API
def transcribe_audio(file_path, model="whisper-large-v3"):
    with open(file_path, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model=model,
            response_format="verbose_json",
        )
    return transcription.text

# Function to translate text using Groq Chat Completion model
def translate_to_english(text):
    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "Translate this to English: {text}. Only output the translation."
            },
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
    )
    translation = "".join(chunk.choices[0].delta.content for chunk in completion)
    return translation.strip()

# Function to convert text to speech using gTTS
def play_audio_with_gtts(text, output_file="output_audio.mp3"):
    tts = gTTS(text)
    tts.save(output_file)
    return output_file

# Streamlit app interface
st.title("Any Language to English Translator")
st.write("Record audio, transcribe it, and translate to English.")

# Record audio
if st.button("Record Audio"):
    audio_file = record_audio()
    st.audio(audio_file, format="audio/wav")

    # Transcribe audio
    st.write("Transcribing audio...")
    try:
        transcription = transcribe_audio(audio_file)
        st.write("### Transcription:")
        st.write(transcription)

        # Translate transcription
        st.write("Translating to English...")
        translation = translate_to_english(transcription)
        st.write("### Translation:")
        st.write(translation)

        # Convert translation to audio
        st.write("Converting translation to speech...")
        response_audio = play_audio_with_gtts(translation)
        st.audio(response_audio, format="audio/mp3")

    except Exception as e:
        st.error(f"An error occurred: {e}")
