# Audio Summarizer

This application provides a simple interface for users to upload MP3 files and get a summary of the audio content using Google's Gemini 1.5 Flash model.

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google API key as an environment variable:
   ```
   export GOOGLE_API_KEY='your-api-key-here'
   ```
4. Run the Streamlit app:
   ```
   streamlit run Audio_Summarizer.py
   ```

## Usage

1. Upload an MP3 file through the web interface.
2. The app will process the audio and provide a summary of its content.

Note: Users need to provide their own Google API key to use this application.

## Disclaimer

Ensure you have the necessary rights to process and summarize the audio content you upload.
