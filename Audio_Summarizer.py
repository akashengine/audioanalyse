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

def main():
    st.set_page_config(page_title="Drishti IAS Call Analysis AI", page_icon="📞", layout="wide")
    
    st.title("📞 Drishti IAS Call Analysis AI")
    st.write("Upload an MP3 file of a customer support call to get a transcript and quality metrics.")
    
    # Custom CSS for conversation style
    st.markdown("""
    <style>
    .conversation-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
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
    
    uploaded_file = st.file_uploader("Choose an MP3 file", type="mp3")
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Analyze Call", key="analyze_button"):
            with st.spinner("Analyzing call..."):
                # ... (analysis process remains the same)
                
                # For demonstration, let's use the transcript and analysis from the image
                transcript = "Agent: (0:13) हाँ नमस्कार सर Student: (0:15) नमस्कार Agent: (0:17) हम सर Student: (0:18) मैं यह दृष्टि Agent: (0:19) आईएसस का स्टूडेंट Student: (0:20) विंडोज फाउंडेशन बैच Agent: (0:21) 42 का [Student: (0:25) मुझे] मुझे विंडोज Agent: (0:27) मैं मुझे अपना डिवाइस Student: (0:28) चेंज करना था उसके लिए Agent: (0:29) नए डिवाइस पे शिफ्ट Student: (0:30) चाहिए था Agent: (0:32) नए डिवाइस Student: (0:33) पे क्या कहते हैं उस पे शिफ्ट Agent: (0:34) पे शिफ्ट मतलब विंडोज में लॉग इन करना Student: (0:36) है नए डिवाइस अगर पुराने डिवाइस पे लॉग इन है वो Agent: (0:38) बदल रहा हूँ मैं Agent: (0:43) मोबाइल नंबर बताइए Student: (0:46) 98 Agent: (0:49) 28 Student: (0:51) हाँ 9828 Agent: (0:52) हाँ Student: (0:54) 33 Agent: (0:56) हाँ Student: (0:56) 89 Agent: (0:58) हाँ Student: (0:59) 37 Agent: (0:60) 89 Student: (0:62) 3 Agent: (0:63) 7 Agent: (0:66) मयंक शर्मा Student: (0:68) जी मयंक शर्मा लैपटॉप में एक्सेस चाहिए था Agent: (0:70) हाँ विंडोज में Agent: (0:117) ठीक है ठीक Agent: (0:119) है लॉग इन कर लीजिए Student: (0:122) कितना टाइम लगेगा सर? Student: (0:124) आप कभी कर लीजिएगा अगर Agent: (0:126) अच्छा अच्छा भी कर सकता हूँ मैं Agent: (0:127) ठीक है कर रहा हूँ Agent: (0:130) ट्राई करो सर Student: (0:133) ठीक है सर ओके Agent: (0:134) ट्राई करो Agent: (0:136) ठीक है सर Student: (0:139) हाँ ओके बाई Student: (0:40) ओके ओके ठीक यू ठीक यू"
                
                analysis = {
                    "Call Duration": "1 minute 40 seconds",
                    "Customer Name": "Drishti",
                    "Customer ID/Batch": "Windows Foundation Batch 42",
                    "Product/Service": "IAS Preparation Course",
                    "Call Reason": "Device change for course access",
                    "Problem Resolution Status": "Resolved",
                    "Hold Time": "Not specified",
                    "Agent Greeting": "हाँ नमस्कार सर",
                    "Customer Effort": "Low",
                    "Customer Sentiment": "Neutral"
                }
                
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
                    st.write("A student from Drishti IAS, Windows Foundation Batch 42, called for assistance with changing devices for course access. The agent provided guidance on logging in to the new device.")
                    
                    st.write("### Call Quality Metrics")
                    metrics_df = pd.DataFrame.from_dict(analysis, orient='index', columns=['Value'])
                    metrics_df.index.name = 'Metric'
                    st.table(metrics_df)

if __name__ == "__main__":
    main()
