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
    background-color: #159f22;
}
</style>
""", unsafe_allow_html=True)

def process_audio(audio_file):
    try:
        uploaded_file = genai.upload_file(audio_file)
        model = genai.GenerativeModel('models/gemini-1.5-pro')
        
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
            Ensure each line of dialogue is in a separate div with the appropriate class.
        """
        transcript_response = model.generate_content([transcript_prompt, uploaded_file])
        transcript_html = transcript_response.text
        
        analysis_prompt = """
            Based on the following customer support call transcript, please provide:
            1. A brief summary of the call (2-3 sentences)
            2. Analyze the call based on the following fixed parameters:
               - Call Duration
               - Customer Name
               - Customer ID/Batch
               - Customer Mobile Number (Extract this from the transcript, regardless of the language used)
               - Product/Service
               - Call Reason
               - Problem Resolution Status
               - Hold Time
               - Agent Greeting
               - Customer Effort
               - Customer Sentiment
            
            Provide the analysis as an HTML table with the following structure:
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
            
            Include a separate section for the call summary:
            <h3>Call Summary</h3>
            <p>Summary text here</p>
            
            Important notes:
            1. For the Customer Mobile Number, carefully extract it from the transcript. It may be spoken in any language, including Hindi numerals. Convert it to standard digits if necessary.
            2. If the mobile number is not explicitly mentioned in the call, indicate "Not provided in call" for this field.
            3. Ensure all Hindi text in the analysis is preserved in Devanagari script.
            
            Ensure the HTML is properly formatted and can be directly rendered in a web page.
            """
        analysis_response = model.generate_content([analysis_prompt, transcript_html])
        analysis_html = analysis_response.text
        
        return transcript_html, analysis_html
    except Exception as e:
        st.error(f"Error in process_audio: {str(e)}")
        return None, None

def calculate_tokens_and_insights(model, transcript_html, analysis_html):
    try:
        transcript_tokens = model.count_tokens(transcript_html).total_tokens
        analysis_tokens = model.count_tokens(analysis_html).total_tokens
        total_tokens = transcript_tokens + analysis_tokens

        # Extract call duration from the analysis HTML
        call_duration_match = re.search(r'<td>Call Duration</td>\s*<td>(.*?)</td>', analysis_html)
        call_duration = call_duration_match.group(1) if call_duration_match else "Unknown"

        # Calculate tokens per minute
        try:
            duration_parts = call_duration.split()
            minutes = int(duration_parts[0])
            tokens_per_minute = total_tokens / minutes if minutes > 0 else 0
        except:
            tokens_per_minute = 0

        insights = {
            "Total Tokens": total_tokens,
            "Transcript Tokens": transcript_tokens,
            "Analysis Tokens": analysis_tokens,
            "Tokens per Minute": f"{tokens_per_minute:.2f}",
            "Call Duration": call_duration
        }

        return insights
    except Exception as e:
        return {"Error": str(e)}

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
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                start_time = time.time()
                
                with st.status("Analyzing call...", expanded=True) as status:
                    status.update(label="Initializing...", state="running", expanded=True)
                    time.sleep(1)  # Simulate initialization time
                    
                    status.update(label="Generating transcript...", state="running")
                    transcript_progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.1)  # Simulate transcript generation time
                        transcript_progress.progress(i + 1)
                    transcript_html, _ = process_audio(temp_file_path)
                    
                    status.update(label="Analyzing call...", state="running")
                    analysis_progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.1)  # Simulate analysis time
                        analysis_progress.progress(i + 1)
                    _, analysis_html = process_audio(temp_file_path)
                    
                    status.update(label="Calculating insights...", state="running")
                    model = genai.GenerativeModel('models/gemini-1.5-pro')
                    insights = calculate_tokens_and_insights(model, transcript_html, analysis_html)
                    
                    status.update(label="Analysis complete!", state="complete")

                end_time = time.time()
                
                if transcript_html and analysis_html:
                    st.success(f"Analysis completed in {end_time - start_time:.2f} seconds.")
                    
                    with transcript_placeholder:
                        st.markdown(transcript_html, unsafe_allow_html=True)
                    
                    with analysis_placeholder:
                        st.markdown(analysis_html, unsafe_allow_html=True)
                    
                    st.subheader("Token Insights")
                    if "Error" in insights:
                        st.error(f"An error occurred while calculating token insights: {insights['Error']}")
                    else:
                        for key, value in insights.items():
                            st.metric(key, value)
                else:
                    st.error("Failed to process the audio file. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
