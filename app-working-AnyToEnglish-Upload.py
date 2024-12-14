import os
from groq import Groq
from gtts import gTTS
from pydub import AudioSegment
import streamlit as st

# Initialize the Groq client
API_KEY = "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"
client = Groq(api_key=API_KEY)

# Function to transcribe audio using Groq Whisper API
def transcribe_audio(file_path, model="whisper-large-v3"):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), file.read()),
            model=model,
            response_format="verbose_json",
        )
    return transcription

# Function to play audio with gTTS
def play_audio_with_gtts(text, output_file="output_audio.mp3"):
    tts = gTTS(text)
    tts.save(output_file)
    return output_file

# Function to translate text using Groq Chat Completion model
def translate_to_english(text):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": f"translate this to english: {text}\nOnly output the translation."
            },
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    # Collect the translation response
    translation = ""
    for chunk in completion:
        translation += chunk.choices[0].delta.content or ""

    return translation.strip()

# Streamlit App
st.title("Audio Transcription and Translation")

# Step 1: Upload an audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file:
    st.success(f"Uploaded file: {uploaded_file.name}")

    # Save the uploaded file to a temporary location
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.read())

    # Convert to a supported format if needed (e.g., .wav)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    if file_extension not in [".mp3", ".wav"]:
        st.write("Converting audio file to .wav format...")
        sound = AudioSegment.from_file(temp_file_path)
        temp_file_path = "converted_audio.wav"
        sound.export(temp_file_path, format="wav")
        st.write("Conversion complete.")

    # Step 2: Transcribe the audio
    st.write("Transcribing audio...")
    try:
        transcription = transcribe_audio(temp_file_path)

        # Access transcription text and language attributes
        transcription_text = transcription.text
        transcription_language = transcription.language

        st.subheader("Transcription Results:")
        st.text(transcription_text)

        # Check if the transcription is not in English
        if transcription_language != "en":
            st.write("\nTranscription is not in English. Translating to English...")

            # Translate the transcription to English
            try:
                translated_text = translate_to_english(transcription_text)
                st.subheader("Translated Text:")
                st.text(translated_text)

                # Play the translated text as speech
                st.write("\nPlaying the translation as speech:")
                translated_audio_output = play_audio_with_gtts(translated_text, "translated_output_audio.mp3")
                st.audio(translated_audio_output, format="audio/mp3")
            except Exception as e:
                st.error(f"An error occurred during translation: {e}")
        else:
            # If the transcription is already in English, play it directly
            st.write("\nTranscription is already in English. Playing the transcription as speech:")
            audio_output = play_audio_with_gtts(transcription_text)
            st.audio(audio_output, format="audio/mp3")

    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

    # Clean up temporary file
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)