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
.conversation-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    background-color: #f0f0f0;
    border-radius: 10px;
}
.message {
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
    margin-bottom: 10px;
}
.agent {
    align-self: flex-start;
    background-color: #e1f3fd;
    color: #000000;
}
.student {
    align-self: flex-end;
    background-color: #dcf8c6;
    color: #000000;
}
.time {
    font-size: 0.8em;
    color: #666;
    margin-bottom: 5px;
}
.stSpinner { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

def format_transcript(transcript):
    # Split the transcript into lines
    lines = transcript.split('\n')
    formatted_html = '<div class="conversation-container">'
    
    for line in lines:
        # Use regex to match the speaker, timestamp, and content
        match = re.match(r'(Agent|Student): \((\d+:\d+)\) (.+)', line)
        if match:
            speaker, time, content = match.groups()
            css_class = speaker.lower()
            formatted_html += f'''
            <div class="message {css_class}">
                <div class="time">{time}</div>
                <div>{content}</div>
            </div>
            '''
    
    formatted_html += '</div>'
    return formatted_html

def process_audio(audio_file):
    try:
        uploaded_file = genai.upload_file(audio_file)
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        transcript_prompt = """
        Transcribe the following audio file completely and accurately.
        Format the transcript as a conversation between Agent and Student.
        Preserve any Hindi text in Devanagari script, and use English for English speech.
        Include timestamps for each dialogue line in the format (MM:SS).
        Return the transcript as plain text with each line in the format:
        Speaker: (timestamp) content
        """
        transcript_response = model.generate_content([transcript_prompt, uploaded_file])
        transcript_text = transcript_response.text
        
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
        """
        analysis_response = model.generate_content([analysis_prompt, transcript_text])
        analysis_html = analysis_response.text
        
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
                with transcript_placeholder:
                    with st.spinner("Generating transcript..."):
                        time.sleep(0.1)  # Ensure spinner is displayed

            with col2:
                st.subheader("Call Analysis")
                analysis_placeholder = st.empty()
                with analysis_placeholder:
                    with st.spinner("Analyzing call..."):
                        time.sleep(0.1)  # Ensure spinner is displayed
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                start_time = time.time()
                transcript_text, analysis_html = process_audio(temp_file_path)
                end_time = time.time()
                
                if transcript_text and analysis_html:
                    st.success(f"Analysis completed in {end_time - start_time:.2f} seconds.")
                    
                    with transcript_placeholder:
                        formatted_transcript = format_transcript(transcript_text)
                        st.markdown(formatted_transcript, unsafe_allow_html=True)
                    
                    with analysis_placeholder:
                        st.markdown(analysis_html, unsafe_allow_html=True)
                else:
                    st.error("Failed to process the audio file. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
