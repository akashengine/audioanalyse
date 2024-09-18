import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def process_audio(audio_file):
    uploaded_file = genai.upload_file(audio_file)
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    
    # Generate transcript
    transcript_prompt = "Transcribe the following audio file completely and accurately."
    transcript_response = model.generate_content([transcript_prompt, uploaded_file])
    transcript = transcript_response.text
    
    # Generate summary and metrics
    analysis_prompt = """
    Based on the following customer support call transcript, please provide:
    1. A brief summary of the call (2-3 sentences)
    2. 10 metrics to evaluate the call quality, presented as a list of key-value pairs.
    Include metrics such as call duration, problem resolution status, customer satisfaction score, etc.
    """
    analysis_response = model.generate_content([analysis_prompt, transcript])
    analysis = analysis_response.text
    
    return transcript, analysis

def main():
    st.title("Customer Support Call Analyzer")
    st.write("Upload an MP3 file of a customer support call to get a transcript and quality metrics.")

    uploaded_file = st.file_uploader("Choose an MP3 file", type="mp3")

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')

        if st.button("Analyze Call"):
            with st.spinner("Analyzing call..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name

                try:
                    transcript, analysis = process_audio(temp_file_path)
                    
                    st.subheader("Transcript:")
                    st.text_area("Full Transcript", transcript, height=300)
                    
                    st.subheader("Call Analysis:")
                    summary, metrics = analysis.split("2.", 1)
                    st.write(summary.strip())
                    
                    st.subheader("Call Quality Metrics:")
                    metrics_list = metrics.strip().split("\n")
                    metrics_dict = {m.split(":")[0].strip(): m.split(":")[1].strip() for m in metrics_list if ":" in m}
                    st.table(metrics_dict)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
