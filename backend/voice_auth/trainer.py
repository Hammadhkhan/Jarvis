# backend/voice_auth/trainer.py
import os
import glob
from pyAudioAnalysis import audioTrainTest as aT
import shutil

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

SAMPLES_PARENT_DIR = "backend/voice_auth/samples/" 
USER_SAMPLES_DIR = os.path.join(SAMPLES_PARENT_DIR, "user_1")
MODELS_DIR = "backend/voice_auth/models/"
MODEL_NAME_BASE = os.path.join(MODELS_DIR, "user_1_voice_model") 
ST_WIN = 0.050  # Short-term window size (seconds)
ST_STEP = 0.025 # Short-term window step (seconds)

def train_voice_model():
    eel_show_info("Starting voice model training...")
    speak("Starting voice model training. This may take a few moments.")

    if not os.path.exists(USER_SAMPLES_DIR) or not os.listdir(USER_SAMPLES_DIR):
        error_msg = f"Error: Samples directory {USER_SAMPLES_DIR} is empty or does not exist."
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        return False

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"Created directory: {MODELS_DIR}")

    # list_of_speaker_dirs should contain the path to user_1 directory
    list_of_speaker_dirs = [USER_SAMPLES_DIR]
    
    # Check if USER_SAMPLES_DIR actually exists and is a directory
    if not os.path.isdir(USER_SAMPLES_DIR):
        error_msg = f"Error: User sample directory {USER_SAMPLES_DIR} not found or not a directory."
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        return False
            
    print(f"Training with speaker directories: {list_of_speaker_dirs}")
    
    try:
        # Clean up old model files if they exist
        for f_item in glob.glob(MODEL_NAME_BASE + "*"): 
            print(f"Deleting old model file: {f_item}")
            if os.path.isdir(f_item): 
                shutil.rmtree(f_item)
            else: 
                os.remove(f_item)

        print(f"Starting training for model: {MODEL_NAME_BASE} using SVM classifier.")
        # pyAudioAnalysis's extract_features_and_train expects a list of directories,
        # where each directory name is the class label and contains samples for that class.
        # For single speaker verification, we often train a model for that one speaker.
        # If we want to use extract_features_and_train, SAMPLES_PARENT_DIR should contain "user_1"
        # and list_of_speaker_dirs should be [os.path.join(SAMPLES_PARENT_DIR, "user_1")]
        # The function call should be:
        # aT.extract_features_and_train([USER_SAMPLES_DIR], मिड_विंडो, मिड_स्टेप, शॉर्ट_विंडो, शॉर्ट_स्टेप, क्लासिफायर_प्रकार, मॉडल_नाम)
        # The first argument is a list of paths to directories. Each directory contains samples of a class.
        # The name of the directory is taken as the class label.
        # So, if USER_SAMPLES_DIR is "backend/voice_auth/samples/user_1/", this structure is correct.
        
        aT.extract_features_and_train(list_of_speaker_dirs, 
                                   1.0, 1.0, # Mid-term window and step (1.0, 1.0 means features per file)
                                   ST_WIN, ST_STEP,   # Short-term window and step
                                   "svm",             # Classifier type (e.g., svm, knn, randomforest)
                                   MODEL_NAME_BASE,   # Output model path (base name)
                                   False)            # Compute beat (False for this task)
        
        model_file_found = any(glob.glob(MODEL_NAME_BASE + "*")) # Check if .svm or other model files created
        
        if model_file_found:
            success_msg = f"Voice model trained successfully and saved as {MODEL_NAME_BASE}*"
            eel_show_info(success_msg)
            speak(success_msg)
            print(success_msg)
            return True
        else:
            error_msg = f"Model training completed, but no model file found for {MODEL_NAME_BASE}."
            eel_show_info(error_msg)
            speak(error_msg)
            print(error_msg)
            return False
            
    except Exception as e:
        error_msg = f"An error occurred during model training: {e}"
        eel_show_info(error_msg)
        speak(error_msg)
        print(error_msg)
        return False

if __name__ == '__main__':
    print("Running voice model training script directly for testing...")
    # Ensure SAMPLES_DIR (specifically USER_SAMPLES_DIR) has some sample .wav files before running.
    # Example: Create backend/voice_auth/samples/user_1/ and put some .wav files in it.
    if train_voice_model():
        print("Voice model training test completed successfully.")
    else:
        print("Voice model training test failed.")
