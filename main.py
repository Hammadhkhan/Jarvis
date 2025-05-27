# main.py
import os
import eel

from backend.voice_auth.utils import delete_existing_voice_data
from backend.voice_auth.enrollment import collect_voice_samples
from backend.voice_auth.trainer import train_voice_model
from backend.voice_auth.verification import verify_voice

from backend.feature import play_assistant_sound
from backend.command import speak

VOICE_MODEL_PRIMARY_FILE = "backend/voice_auth/models/user_1_voice_model.svm_classifier_MEANS" 

@eel.expose
def handle_voice_enrollment_decision(consent):
    if consent:
        speak("Starting new voice enrollment process.")
        eel.showInfo("Enrollment: Starting...")
        delete_existing_voice_data()
        speak("Old voice data cleared. Starting sample collection.")
        eel.showInfo("Enrollment: Collecting voice samples...")
        if collect_voice_samples():
            speak("Voice samples collected. Now training the voice model.")
            eel.showInfo("Enrollment: Training voice model...")
            if train_voice_model():
                speak("Voice model trained. Proceeding with voice verification.")
                eel.showInfo("Enrollment: Complete! Verifying voice...")
                attempt_voice_authentication()
            else:
                speak("Failed to train voice model. Please try enrollment again.")
                eel.showError("Enrollment Error: Could not train model.")
                eel.askForVoiceEnrollment()
        else:
            speak("Failed to collect voice samples. Please ensure microphone is working.")
            eel.showError("Enrollment Error: Could not collect samples.")
            eel.askForVoiceEnrollment()
    else:
        speak("Voice enrollment declined. Jarvis cannot start without authentication.")
        eel.showError("Enrollment Declined: Jarvis cannot start.")

def attempt_voice_authentication():
    speak("Ready for Voice Authentication.")
    eel.showInfo("Authenticating: Please wait...")
    authenticated = verify_voice() 
    if authenticated:
        speak("Voice recognized successfully.")
        eel.showInfo("Authentication Successful!")
        speak("Welcome to Your Assistant.")
        eel.hideStart() 
        play_assistant_sound()
    else:
        speak("Voice not recognized.")
        eel.showError("Authentication Failed: Voice not recognized.")
        if not os.path.exists(VOICE_MODEL_PRIMARY_FILE):
            speak("No recognized voice is enrolled. Please enroll your voice.")
            eel.showInfo("Info: No voice enrolled. Please enroll.")
            eel.askForVoiceEnrollment()
        else:
            speak("Please try voice authentication again.")
            eel.showInfo("Retry voice authentication or restart.")

def start():
    eel.init("frontend") 
    @eel.expose
    def init_jarvis():
        if not os.path.exists(VOICE_MODEL_PRIMARY_FILE):
            play_assistant_sound() 
            speak("No voice data found. Enrollment is required to use Jarvis.")
            eel.showInfo("Welcome! No voice data found. Enrollment is required.")
            eel.askForVoiceEnrollment()
        else:
            play_assistant_sound()
            attempt_voice_authentication()
    os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"') 
    eel.start("index.html", mode=None, host="localhost", block=True)
