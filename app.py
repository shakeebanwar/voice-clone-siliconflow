import streamlit as st
import os
from dotenv import load_dotenv
from core.voice_manager import SiliconFlowVoiceManager

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SILICONFLOW_API_KEY")

st.set_page_config(
    page_title="Voice Clone Studio",
    page_icon="🎙️",
    layout="centered"
)

# Custom Styling (Minimalist & Professional)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎙️ Voice Clone Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate high-quality speech from your cloned voices instantly.</div>', unsafe_allow_html=True)

if not API_KEY:
    st.error("API Key not found! Please check your `.env` file and set `SILICONFLOW_API_KEY`.")
    st.stop()

# Initialize Voice Manager
voice_manager = SiliconFlowVoiceManager(api_key=API_KEY)

@st.cache_data(ttl=300)
def fetch_voices():
    response = voice_manager.list_voices()
    if not response:
        return []
    
    # Handle different JSON structures dynamically
    if isinstance(response, list):
        if len(response) > 0 and isinstance(response[0], dict) and "result" in response[0]:
            return response[0]["result"]
        return response
    elif isinstance(response, dict):
        # Look for standard keys that might hold the list of voices
        for key in ["data", "voices", "items", "result"]:
            if key in response and isinstance(response[key], list):
                return response[key]
        return [response]  # Fallback
    return []

voices = fetch_voices()

if not voices:
    st.warning("No voices found or failed to fetch voices.")
    st.stop()

# Create a mapping for the dropdown
voice_options = {}
for v in voices:
    # Show only the custom name in the dropdown, but map it to its URI
    name = v.get("customName") or v.get("name") or "Unknown Voice"
    uri = v.get("uri")
    if uri:
        # Handle potential duplicates in custom names nicely
        display_name = name
        counter = 1
        while display_name in voice_options:
            display_name = f"{name} ({counter})"
            counter += 1
        voice_options[display_name] = uri

if not voice_options:
    st.warning("Could not parse voice format. Check API response structure.")
    with st.expander("Show raw API response"):
        st.json(voices)
    st.stop()

# UI Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Settings")
    selected_voice_label = st.selectbox("Select Voice Model", options=list(voice_options.keys()))
    selected_uri = voice_options[selected_voice_label]
    
    playback_speed = st.slider(
        "Playback Speed (1.0x to 2.0x)", 
        min_value=1.0, 
        max_value=2.0, 
        value=1.0, 
        step=0.1
    )
    
    st.info("Voices are dynamically fetched from your SiliconFlow account.")

with col2:
    st.subheader("📝 Input Text")
    input_text = st.text_area(
        "Enter text to synthesize",
        height=200,
        placeholder="Type or paste your text here to generate audio..."
    )

st.markdown("---")

model_name = "fishaudio/fish-speech-1.5"
output_filename = "generated_audio.mp3"

if st.button("🚀 Generate Audio", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("Please enter some text to generate audio.")
    else:
        with st.spinner("Synthesizing speech..."):
            success = voice_manager.generate_speech(
                model=model_name,
                input_text=input_text,
                voice_uri=selected_uri,
                output_path=output_filename,
                speed=playback_speed
            )
        
        if success:
            st.success("✅ Audio generated successfully!")
            
            # Read and play audio
            with open(output_filename, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            st.audio(audio_bytes, format="audio/mp3")
            
            # Download Button
            st.download_button(
                label="📥 Download MP3",
                data=audio_bytes,
                file_name="generated_voice.mp3",
                mime="audio/mp3",
                type="primary"
            )
        else:
            st.error("❌ Failed to generate audio. Please check the logs or API credentials.")
