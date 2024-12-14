import streamlit as st
from groq import Groq
from gtts import gTTS
from deepgram import Deepgram

# Initialize Groq client
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Deepgram client
DEEPGRAM_API_KEY = "805291bd449136dca714e320d57d53476efdcc13"
deepgram_client = Deepgram("805291bd449136dca714e320d57d53476efdcc13")

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
                "content": f"Translate this to English: {text}. Only output the translation."
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
st.write("Upload an audio file, transcribe it, and translate to English.")

# Upload audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    file_path = f"uploaded_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.audio(file_path, format=f"audio/{uploaded_file.type}")

    # Transcribe audio
    st.write("Transcribing audio...")
    try:
        transcription = transcribe_audio(file_path)
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
