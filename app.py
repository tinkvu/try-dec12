import streamlit as st
import pyaudio
import wave
import os
from groq import Groq
from gtts import gTTS

# Initialize Groq client
API_KEY = "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"
client = Groq(api_key=API_KEY)

# Function to record audio
def record_audio(duration=5, filename="recorded_audio.wav"):
    chunk = 1024  # Record in chunks of 1024 samples
    format = pyaudio.paInt16  # 16 bits per sample
    channels = 2  # 2 channels for stereo
    rate = 44100  # Sample rate
    p = pyaudio.PyAudio()

    # Start recording
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    frames = []

    st.write("Recording...")
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    st.write("Recording complete.")
    
    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    return filename

# Function to transcribe audio
def transcribe_audio(file_path, model="whisper-large-v3"):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model=model,
            response_format="verbose_json",
        )
    return transcription

# Function to convert text to speech
def text_to_speech(text, output_file="output_audio.mp3"):
    tts = gTTS(text)
    tts.save(output_file)
    return output_file

# Streamlit app layout
st.title("English Language Trainer")

# Record audio
if st.button("Record Audio"):
    audio_file = record_audio(duration=5)

    # Transcribe audio
    st.write("Transcribing audio...")
    transcription = transcribe_audio(audio_file)
    transcription_text = transcription.text if transcription else "Transcription failed."
    st.write("Transcription Results:")
    st.write(transcription_text)

    # Convert transcription to speech
    if transcription_text:
        st.write("Generating speech...")
        audio_output = text_to_speech(transcription_text)
        st.audio(audio_output)

# Run the app
if __name__ == "__main__":
    st.write("Press the button above to start recording.")
