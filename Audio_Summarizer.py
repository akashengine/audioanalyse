import streamlit as st
import pandas as pd
import re
import tempfile
import os
from dotenv import load_dotenv
import time
import json
import google.generativeai as genai

# Ensure set_page_config is called first
st.set_page_config(page_title="Drishti IAS Call Analysis AI", page_icon="📞", layout="wide")

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Custom CSS for conversation style
st.markdown("""
<style>
.conversation-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 500px;
    overflow-y: auto;
}
.message {
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
}
.agent {
    align-self: flex-start;
    background-color: #e1f3fd;
}
.student {
    align-self: flex-end;
    background-color: #dcf8c6;
}
.time {
    font-size: 0.8em;
    color: #888;
}
</style>
""", unsafe_allow_html=True)

def format_transcript_conversation(transcript):
    lines = transcript.split('\n')
    formatted_transcript = []
    for line in lines:
        if line.strip():
            match = re.match(r'(Agent|Student): \((\d+:\d+)\) (.+)', line)
            if match:
                speaker, time, text = match.groups()
                formatted_transcript.append({
                    'speaker': speaker,
                    'time': time,
                    'text': text
                })
    return formatted_transcript

def process_audio(audio_file):
    try:
        st.text("Uploading file...")
        uploaded_file = genai.upload_file(audio_file)
        st.text("File uploaded successfully.")
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        st.text("Generating transcript...")
        transcript_prompt = """
        Transcribe the following audio file completely and accurately.
        Format the transcript as a conversation between Agent and Student.
        Preserve any Hindi text in Devanagari script, and use English for English speech.
        Include timestamps for each dialogue line in the format (MM:SS).
        """
        transcript_response = model.generate_content([transcript_prompt, uploaded_file])
        transcript = transcript_response.text
        st.text("Transcript generated successfully.")
        
        st.text("Analyzing call...")
        analysis_prompt = """
        Based on the following customer support call transcript, please provide:
        1. A brief summary of the call (2-3 sentences)
        2. Analyze the call based on the following fixed parameters:
           - Call Duration
           - Customer Name
           - Customer ID/Batch
           - Product/Service
           - Call Reason
           - Problem Resolution Status
           - Hold Time
           - Agent Greeting
           - Customer Effort
           - Customer Sentiment
        
        Provide the analysis as a JSON object with these keys and their corresponding values based on the call context.
        """
        analysis_response = model.generate_content([analysis_prompt, transcript])
        analysis = json.loads(analysis_response.text)
        st.text("Analysis completed.")
        
        return transcript, analysis
    except Exception as e:
        st.error(f"Error in process_audio: {str(e)}")
        return None, None

def main():
    st.title("📞 Drishti IAS Call Analysis AI")
    st.write("Upload an MP3 file of a customer support call to get a transcript and quality metrics.")
    
    uploaded_file = st.file_uploader("Choose an MP3 file", type="mp3")
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Analyze Call", key="analyze_button"):
            with st.spinner("Analyzing call..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                
                try:
                    start_time = time.time()
                    transcript, analysis = process_audio(temp_file_path)
                    end_time = time.time()
                    
                    if transcript and analysis:
                        st.success(f"Analysis completed in {end_time - start_time:.2f} seconds.")
                        
                        # Split the screen into two columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Transcript")
                            conversation = format_transcript_conversation(transcript)
                            
                            st.markdown('<div class="conversation-container">', unsafe_allow_html=True)
                            for message in conversation:
                                css_class = "message " + message['speaker'].lower()
                                st.markdown(f'<div class="{css_class}">'
                                            f'<div class="time">{message["time"]}</div>'
                                            f'{message["text"]}'
                                            f'</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.subheader("Call Analysis")
                            
                            st.write("### Call Summary")
                            st.write(analysis.get("summary", "No summary available."))
                            
                            st.write("### Call Quality Metrics")
                            metrics = {k: v for k, v in analysis.items() if k != "summary"}
                            metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
                            metrics_df.index.name = 'Metric'
                            st.table(metrics_df)
                    else:
                        st.error("Failed to process the audio file. Please try again.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
