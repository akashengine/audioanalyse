import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
import time
import google.generativeai as genai
import re

# Ensure set_page_config is called first
st.set_page_config(page_title="Drishti IAS Call Analysis AI", page_icon="📞", layout="wide")

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Custom CSS for styling
st.markdown("""
<style>
.transcript-container {
    background-color: #2b2b2b;
    color: #ffffff;
    padding: 10px;
    border-radius: 5px;
    max-height: 500px;
    overflow-y: auto;
}
.transcript-line {
    margin-bottom: 10px;
    font-family: monospace;
}
.agent {
    color: #63c5da;
}
.student {
    color: #98fb98;
}
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #4a4a4a;
    color: white;
}
td {
    background-color: #2b2b2b;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

def format_transcript(transcript):
    lines = transcript.split('\n')
    formatted_html = '<div class="transcript-container">'
    for line in lines:
        match = re.match(r'(Agent|Student): (.+) \((\d+:\d+)-(\d+:\d+)\)', line)
        if match:
            speaker, content, start_time, end_time = match.groups()
            formatted_html += f'<div class="transcript-line {speaker.lower()}"><strong>{speaker}:</strong> {content} <span style="color: #888;">({start_time}-{end_time})</span></div>'
    formatted_html += '</div>'
    return formatted_html

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
        Include start and end timestamps for each dialogue line in the format (MM:SS-MM:SS).
        Return the transcript as plain text with each line in the format:
        Speaker: content (start_time-end_time)
        """
        transcript_response = model.generate_content([transcript_prompt, uploaded_file])
        transcript_text = transcript_response.text
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
        
        Provide the analysis as an HTML table with appropriate styling. 
        Include a separate section for the call summary.
        Ensure the HTML is properly formatted and can be directly rendered in a web page.
        Use <th> for table headers and <td> for table data.
        Include a table header row with 'Parameter' and 'Value' as column headers.
        """
        analysis_response = model.generate_content([analysis_prompt, transcript_text])
        analysis_html = analysis_response.text
        st.text("Analysis completed.")
        
        return transcript_text, analysis_html
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
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transcript")
                transcript_placeholder = st.empty()

            with col2:
                st.subheader("Call Analysis")
                analysis_placeholder = st.empty()

            progress_bar = st.progress(0)
            
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name

                for i in range(101):
                    time.sleep(0.01)
                    progress_bar.progress(i)
                
                # Pass the file path to process_audio
                with open(temp_file_path, 'rb') as audio_file:
                    transcript_text, analysis_html = process_audio(audio_file)
                
                if transcript_text and analysis_html:
                    with transcript_placeholder:
                        formatted_transcript = format_transcript(transcript_text)
                        st.markdown(formatted_transcript, unsafe_allow_html=True)
                    
                    with analysis_placeholder:
                        st.markdown(analysis_html, unsafe_allow_html=True)
                    
                    st.success("Analysis completed successfully!")
                else:
                    st.error("Failed to process the audio file. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                progress_bar.empty()
                if 'temp_file_path' in locals():
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
