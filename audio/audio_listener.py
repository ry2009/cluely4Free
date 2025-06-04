import whisper
import sounddevice as sd
import numpy as np
import logging
import time
import ssl
import os

# Initialize Whisper model (base model for good balance of speed/accuracy)
model = None

def initialize_whisper():
    """Initialize Whisper model on first use with SSL fix"""
    global model
    if model is None:
        print("🎙️ Loading Whisper model...")
        
        try:
            # Fix SSL issues for any future downloads
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Try to load from local models directory first
            model = whisper.load_model("base", download_root="./models")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"⚠️ Error loading Whisper model: {e}")
            print("🔄 Trying fallback approach...")
            
            try:
                # Fallback: load model from default location
                model = whisper.load_model("base")
                print("✅ Whisper model loaded (fallback)")
            except Exception as e2:
                print(f"❌ Failed to load Whisper model: {e2}")
                print("🎙️ Audio transcription will be disabled")
                model = None
    
    return model

def listen_and_transcribe(seconds=5, silence_threshold=0.01):
    """
    Listen to microphone and transcribe speech using Whisper
    
    Args:
        seconds (int): Duration to record in seconds
        silence_threshold (float): Minimum audio level to consider as speech
    
    Returns:
        str: Transcribed text from audio
    """
    try:
        # Initialize model if needed
        whisper_model = initialize_whisper()
        
        if whisper_model is None:
            print("⚠️ Whisper model not available - skipping transcription")
            return ""
        
        print(f"🎙️ Listening for {seconds} seconds...")
        
        # Record audio from microphone (back to reliable full-duration recording)
        recording = sd.rec(
            int(seconds * 16000), 
            samplerate=16000, 
            channels=1, 
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        
        # Check if there's actual audio content
        audio_data = np.squeeze(recording)
        if np.max(np.abs(audio_data)) < silence_threshold:
            return ""  # Return empty string for silence
        
        # Prepare audio for Whisper
        audio_input = whisper.pad_or_trim(audio_data)
        
        # Transcribe audio
        result = whisper_model.transcribe(audio_input, fp16=False)
        transcribed_text = result['text'].strip()
        
        if transcribed_text:
            print(f"🗣️ Heard: '{transcribed_text}'")
        
        return transcribed_text
        
    except Exception as e:
        logging.error(f"Error in audio transcription: {e}")
        return ""

def test_microphone():
    """Test microphone functionality"""
    print("🎙️ Testing microphone...")
    try:
        # Quick test recording
        test_recording = sd.rec(int(1 * 16000), samplerate=16000, channels=1)
        sd.wait()
        
        max_level = np.max(np.abs(test_recording))
        print(f"📊 Microphone level: {max_level:.4f}")
        
        if max_level > 0.001:
            print("✅ Microphone working properly")
            return True
        else:
            print("⚠️ Microphone level very low - check connection")
            return False
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False 