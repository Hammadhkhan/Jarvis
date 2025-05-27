import os
import eel
from backend.auth.utils import delete_existing_face_data
from backend.auth.sample import collect_face_samples
from backend.auth.trainer import train_face_model
from backend.auth import recoganize # Ensure this is how AuthenticateFace is accessed
from backend.feature import play_assistant_sound # Keep existing necessary imports
from backend.command import speak # Keep existing necessary imports

TRAINER_FILE_PATH = "backend/auth/trainer/trainer.yml"

@eel.expose
def handle_face_registration_decision(consent):
    if consent:
        speak("Starting new face registration process.")
        eel.showInfo("Registration: Starting...") # JS function to show message on UI

        delete_existing_face_data() # This function should handle clearing SAMPLES_PATH and TRAINER_FILE_PATH
        speak("Old face data cleared. Starting sample collection.")
        eel.showInfo("Registration: Collecting samples...")

        if collect_face_samples():
            speak("Face samples collected successfully. Now training the model.")
            eel.showInfo("Registration: Training model...")
            if train_face_model():
                speak("Face model trained successfully. Proceeding with authentication.")
                eel.showInfo("Registration: Complete! Authenticating...")
                attempt_face_authentication()
            else:
                speak("Failed to train face model. Please try registration again.")
                eel.showError("Registration Error: Could not train model.")
                eel.askForFaceRegistration() # Ask again
        else:
            speak("Failed to collect face samples. Please ensure your camera is working and try again.")
            eel.showError("Registration Error: Could not collect samples.")
            eel.askForFaceRegistration() # Ask again
    else:
        speak("Face registration declined. Jarvis cannot start without authentication.")
        eel.showError("Registration Declined: Jarvis cannot start.")
        # Consider eel.closeWindow() or disabling UI further. For now, it just informs.

def attempt_face_authentication():
    speak("Ready for Face Authentication")
    # Assuming recoganize.AuthenticateFace() handles showing/hiding loader & auth UI elements
    # and returns 1 for success, 0 for failure.
    flag = recoganize.AuthenticateFace() 
    
    if flag == 1: # Authentication successful
        speak("Face recognized successfully")
        eel.hideFaceAuth() # JS function to hide face auth UI
        if callable(getattr(eel, 'hideFaceAuthSuccess', None)): # Check if JS func exists
            eel.hideFaceAuthSuccess() # JS function for temp success message
        speak("Welcome to Your Assistant")
        if callable(getattr(eel, 'hideStart', None)): # Check if JS func exists
            eel.hideStart() # JS function to hide initial start screen
        play_assistant_sound()
    else: # Authentication failed
        speak("Face not recognized.")
        eel.showError("Authentication Failed: Face not recognized.") # JS function
        
        # Check if this was the first attempt (no trainer file) or a retry
        if not os.path.exists(TRAINER_FILE_PATH):
            speak("No recognized face is registered. Please register a face.")
            eel.showInfo("Info: No face registered. Please register.")
            eel.askForFaceRegistration() # JS function to show registration prompt
        else:
            speak("Please try authentication again.")
            # This implies the UI should allow another attempt.
            # recoganize.AuthenticateFace() might need to be designed to show UI again.
            # Or, a specific JS function could be called to re-show the auth interface.
            if callable(getattr(eel, 'showFaceAuth', None)):
                 eel.showFaceAuth() 
            else: 
                 speak("Please restart the application to try authentication again or to re-register.")

def start():
    eel.init("frontend") 
    # play_assistant_sound() # Moved to be more context-specific

    @eel.expose
    def init_jarvis(): # This is called by JS once the page is ready
        # eel.hideLoader() # Let initial UI (auth/registration) handle its own loader
        
        if not os.path.exists(TRAINER_FILE_PATH):
            play_assistant_sound() 
            speak("No face data found. Registration is required to use Jarvis.")
            eel.showInfo("Welcome! No face data found. Registration is required.") # UI message
            eel.askForFaceRegistration() # JS function to ask yes/no
        else:
            play_assistant_sound() 
            # speak("Welcome to Jarvis") # Moved to after successful auth
            attempt_face_authentication()
    
    # This command is specific to Windows and MS Edge.
    # For broader compatibility, this might need to be handled differently or made configurable.
    # Example: try to open the default browser instead of hardcoding Edge.
    try:
        os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    except Exception as e:
        print(f"Note: Could not launch Edge automatically: {e}. Please open http://localhost:8000 manually.")
    
    eel.start("index.html", mode=None, host="localhost", block=True) # mode=None allows choosing browser
    # Consider 'chrome' or 'default' for mode if Edge is not always preferred/available.
    # eel.start("index.html", mode='chrome', host="localhost", block=True, 
    #           options={'chromeFlags': ['--window-size=1000,800', '--app=http://localhost:8000']})


# Note: main.py is typically not run directly in this project structure.
# run.py usually imports and calls main.start(). So, no `if __name__ == "__main__":` here.
