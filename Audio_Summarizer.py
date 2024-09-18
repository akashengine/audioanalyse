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
    background-color: #f0f0f0;
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
    color: #0066cc;
}
.student {
    color: #006600;
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
thead {
    background-color: #f2f2f2;
}
</style>
""", unsafe_allow_html=True)


def process_audio_chunk(_audio_content, prompt):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        response = model.generate_content([prompt, _audio_content])
        return response.text
    except Exception as e:
        st.error(f"Error in API call: {str(e)}")
        return None

def process_audio(audio_file):
    try:
        audio_content = audio_file.read()
        
        transcript_prompt = """
        Transcribe the following audio file completely and accurately.
        Format the transcript as a conversation between Agent and Student.
        Preserve any Hindi text in Devanagari script, and use English for English speech.
        Do not include any timestamps in the output.
        Return the transcript as HTML with the following structure:
        <div class="transcript-container">
            <div class="transcript-line agent/student">
                <span class="speaker">Speaker:</span>
                <span class="content">content</span>
            </div>
            <!-- Repeat for each line of dialogue -->
        </div>
        Use the "agent" class for Agent lines and "student" class for Student lines.
        """
        
        analysis_prompt = """
        Based on the following customer support call transcript, please provide:
        1. A brief summary of the call (2-3 sentences)
        2. Analyze the call based on the following fixed parameters:
           - Call Duration (estimate based on the conversation)
           - Customer Name
           - Customer ID/Batch
           - Product/Service
           - Call Reason
           - Problem Resolution Status
           - Hold Time
           - Agent Greeting
           - Customer Effort
           - Customer Sentiment
        
        Provide the analysis as an HTML table with the following structure:
        <div class="call-summary">
            <h3>Call Summary</h3>
            <p>Summary text here</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th colspan="2">Call Analysis</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
                <!-- Repeat for each parameter -->
            </tbody>
        </table>
        
        Ensure the HTML is properly formatted and can be directly rendered in a web page.
        """
        
        with st.spinner("Processing audio..."):
            transcript_html = process_audio_chunk(audio_content, transcript_prompt)
            if transcript_html:
                analysis_html = process_audio_chunk(audio_content, analysis_prompt)
            else:
                analysis_html = None
        
        return transcript_html, analysis_html
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
                transcript_html, analysis_html = process_audio(temp_file_path)
                end_time = time.time()
                
                if transcript_html and analysis_html:
                    st.success(f"Analysis completed in {end_time - start_time:.2f} seconds.")
                    
                    with transcript_placeholder:
                        st.markdown(transcript_html, unsafe_allow_html=True)
                    
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
