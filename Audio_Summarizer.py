import streamlit as st
import google.generativeai as genai
import os
import tempfile
from dotenv import load_dotenv
import time
import json

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
                        st.text_area("Full Transcript", transcript, height=300)
                        
                        st.subheader("Call Analysis:")
                        try:
                            analysis_dict = json.loads(analysis)
                            summary = analysis_dict.pop("summary", "No summary available.")
                            st.write(summary)
                            
                            st.subheader("Call Quality Metrics:")
                            metrics_df = pd.DataFrame.from_dict(analysis_dict, orient='index', columns=['Value'])
                            st.table(metrics_df)
                        except json.JSONDecodeError:
                            st.error("Failed to parse the analysis results. Displaying raw output:")
                            st.write(analysis)
                    else:
                        st.error("Failed to process the audio file. Please try again.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
