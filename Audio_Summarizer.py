import streamlit as st
import google.generativeai as genai
from pydub import AudioSegment
import os
import tempfile

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def summarize_audio(audio_file):
    # Upload the audio file
    uploaded_file = genai.upload_file(audio_file)

    # Create a prompt for summarization
    prompt = "Listen carefully to the following audio file. Provide a brief summary."

    # Generate content using Gemini 1.5 Flash
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content([prompt, uploaded_file])

    return response.text

def main():
    st.title("Audio Summarizer")
    st.write("Upload an MP3 file to get a summary of its content.")

    uploaded_file = st.file_uploader("Choose an MP3 file", type="mp3")

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')

        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                # Create a temporary file to store the uploaded audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name

                try:
                    summary = summarize_audio(temp_file_path)
                    st.subheader("Summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
