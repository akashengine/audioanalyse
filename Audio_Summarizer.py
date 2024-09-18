import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv
import time
import json
import pandas as pd
import re
# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
        Include timestamps for each dialogue line.
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
        analysis = analysis_response.text
        st.text("Analysis completed.")
        
        return transcript, analysis
    except Exception as e:
        st.error(f"Error in process_audio: {str(e)}")
        return None, None

import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv
import time
import json
import pandas as pd
import re

# ... (previous code remains the same)

def format_transcript(transcript):
    lines = transcript.split('\n')
    formatted_transcript = []
    for line in lines:
        if line.strip():
            parts = line.split('  ', 1)
            if len(parts) == 2:
                time, text = parts
                formatted_transcript.append(f"**[{time.strip()}]** {text.strip()}")
            else:
                formatted_transcript.append(line)
    return '\n'.join(formatted_transcript)

def parse_analysis(analysis):
    # Split the analysis into summary and JSON parts
    summary_match = re.search(r'## Call Summary:(.*?)## Call Analysis:', analysis, re.DOTALL)
    json_match = re.search(r'```json\s*(.*?)\s*```', analysis, re.DOTALL)
    
    summary = summary_match.group(1).strip() if summary_match else "No summary available."
    
    metrics = {}
    if json_match:
        try:
            metrics = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            st.error("Failed to parse JSON metrics. Displaying raw JSON.")
            st.code(json_match.group(1), language="json")
    
    return summary, metrics

def main():
    st.set_page_config(page_title="Drishti IAS Call Analysis AI", page_icon="📞", layout="wide")
    
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
                        
                        st.subheader("Transcript:")
                        formatted_transcript = format_transcript(transcript)
                        st.markdown(formatted_transcript)
                        
                        st.subheader("Call Analysis:")
                        summary, metrics = parse_analysis(analysis)
                        
                        st.write("### Call Summary")
                        st.write(summary)
                        
                        st.write("### Call Quality Metrics")
                        if metrics:
                            metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
                            metrics_df.index.name = 'Metric'
                            st.table(metrics_df)
                        else:
                            st.warning("No metrics data available.")
                    else:
                        st.error("Failed to process the audio file. Please try again.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
