# backend/voice_auth/verification.py
import os
import sounddevice
import scipy.io.wavfile as wav
import time
import shutil
from pyAudioAnalysis import audioTrainTest as aT
from pyAudioAnalysis import ShortTermFeatures # Though not directly used, good to note for context

# Mock/conditional imports for speak and eel
try:
    from backend.command import speak
except ImportError:
    print("Warning: backend.command.speak not found, using mock speak function.")
    def speak(text): print(f"TTS (mock): {text}")
try:
    import eel
    def eel_show_info(message):
        is_connected = False
        try: is_connected = eel and eel._eel_current_url is not None
        except AttributeError: pass
        if is_connected: eel.showInfo(message)
        else: print(f"EEL (mock - not connected): {message}")
except ImportError:
    eel = None
    print("Warning: eel not found, using mock eel_show_info function.")
    def eel_show_info(message): print(f"EEL (mock - no eel): {message}")

MODELS_DIR = "backend/voice_auth/models/"
MODEL_NAME_BASE = os.path.join(MODELS_DIR, "user_1_voice_model") 
EXPECTED_SPEAKER_LABEL = "user_1" 

SAMPLE_RATE = 16000
DURATION_VERIFICATION_SAMPLE = 4
VERIFICATION_TEMP_DIR = "backend/voice_auth/temp_verification_samples/"
PASSPHRASE = "Hello Jarvis activate"
VERIFICATION_THRESHOLD = 0.7 # Confidence threshold

def verify_voice():
    eel_show_info(f"Preparing for voice verification. Please say '{PASSPHRASE}'.")
    speak(f"Please say the passphrase: {PASSPHRASE}, for voice verification.")

    # Check for a primary model file (e.g., the .svm_classifier_MEANS file)
    primary_model_file_path = MODEL_NAME_BASE + ".svm_classifier_MEANS" 
    if not os.path.exists(primary_model_file_path):
        error_msg = f"Error: Trained voice model file '{primary_model_file_path}' not found. Please enroll first."
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        return False

    if not os.path.exists(VERIFICATION_TEMP_DIR):
        os.makedirs(VERIFICATION_TEMP_DIR)
    
    temp_sample_path = os.path.join(VERIFICATION_TEMP_DIR, "verification_sample.wav")

    for j in range(3, 0, -1):
        eel_show_info(f"Recording in {j}...")
        print(f"Recording in {j}...")
        time.sleep(1)
    
    eel_show_info("Recording now...")
    speak("Recording now.")
    
    try:
        recording = sounddevice.rec(int(DURATION_VERIFICATION_SAMPLE * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sounddevice.wait()
        wav.write(temp_sample_path, SAMPLE_RATE, recording)
        print(f"Verification sample saved to {temp_sample_path}")
    except Exception as e:
        error_msg = f"An error occurred during verification recording: {e}"
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        if os.path.exists(VERIFICATION_TEMP_DIR): shutil.rmtree(VERIFICATION_TEMP_DIR)
        return False

    try:
        eel_show_info("Verifying voice...")
        speak("Verifying your voice.")
        
        # Use MODEL_NAME_BASE for file_classification, pyAudioAnalysis handles extensions.
        winner_class_idx, probability_per_class, class_names = aT.file_classification(temp_sample_path, MODEL_NAME_BASE, "svm")
        
        winner_class_label = class_names[winner_class_idx]
        confidence = probability_per_class[winner_class_idx]

        print(f"Predicted Speaker: {winner_class_label}, Confidence: {confidence:.4f}")
        print(f"All class names from model: {class_names}")
        print(f"Probabilities per class: {probability_per_class}")

        if winner_class_label == EXPECTED_SPEAKER_LABEL and confidence >= VERIFICATION_THRESHOLD:
            success_msg = f"Voice verified successfully as {EXPECTED_SPEAKER_LABEL} with confidence {confidence:.2f}."
            eel_show_info(success_msg)
            speak(success_msg)
            print(success_msg)
            return True
        else:
            fail_msg = f"Voice verification failed. Predicted: {winner_class_label} (Conf: {confidence:.2f}). Expected: {EXPECTED_SPEAKER_LABEL}."
            eel_show_info(fail_msg)
            speak(fail_msg)
            print(fail_msg)
            return False
    except Exception as e:
        error_msg = f"An error occurred during voice verification process: {e}"
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        return False
    finally:
        if os.path.exists(VERIFICATION_TEMP_DIR):
            try:
                shutil.rmtree(VERIFICATION_TEMP_DIR)
                print(f"Cleaned up temporary directory: {VERIFICATION_TEMP_DIR}")
            except Exception as e:
                print(f"Error cleaning up temp directory {VERIFICATION_TEMP_DIR}: {e}")

if __name__ == '__main__':
    print("Running voice verification script directly for testing...")
    # Ensure a model is trained (e.g., user_1_voice_model.svm_classifier_MEANS and .svm_classifier_MEANS.json exist)
    if verify_voice():
        print("Voice verification test SUCCEEDED.")
    else:
        print("Voice verification test FAILED.")
