# backend/voice_auth/enrollment.py
import sounddevice
import scipy.io.wavfile as wav
import os
import time

# Attempt to import speak and eel_showInfo for use when called from main.py
# These will be mocked or handled conditionally if run standalone.
try:
    from backend.command import speak
except ImportError:
    print("Warning: backend.command.speak not found, using mock speak function.")
    def speak(text):
        print(f"TTS (mock): {text}")

try:
    import eel
    def eel_show_info(message):
        # Helper to check if Eel is running and has a current URL
        is_connected = False
        try:
            is_connected = eel and eel._eel_current_url is not None
        except AttributeError: # Handles if eel is None or _eel_current_url doesn't exist
            pass # is_connected remains False
        
        if is_connected:
             eel.showInfo(message) # Assumes showInfo JS function exists
        else:
            print(f"EEL (mock - not connected): {message}")
except ImportError:
    eel = None # Make eel usable in checks like if eel:
    print("Warning: eel not found, using mock eel_show_info function.")
    def eel_show_info(message):
        print(f"EEL (mock - no eel): {message}")

SAMPLES_DIR = "backend/voice_auth/samples/user_1/"
SAMPLE_RATE = 16000  # Hz
DURATION_PER_SAMPLE = 4  # seconds
NUM_SAMPLES_REQUIRED = 5
PASSPHRASE = "Hello Jarvis activate" # Fixed passphrase for consistency

def collect_voice_samples():
    eel_show_info(f"Preparing for voice enrollment. You will be asked to say '{PASSPHRASE}' {NUM_SAMPLES_REQUIRED} times.")
    speak(f"Welcome to voice enrollment. When prompted, please clearly say the passphrase: {PASSPHRASE}.")

    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)
        print(f"Created directory: {SAMPLES_DIR}")
    else:
        print(f"Using existing directory: {SAMPLES_DIR}")

    for i in range(NUM_SAMPLES_REQUIRED):
        sample_num = i + 1
        filename = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.wav")

        prompt_message = f"For sample {sample_num} of {NUM_SAMPLES_REQUIRED}, please say '{PASSPHRASE}'."
        eel_show_info(prompt_message)
        speak(prompt_message)
        
        for j in range(3, 0, -1):
            countdown_message = f"Recording in {j}..."
            eel_show_info(countdown_message)
            print(countdown_message) 
            time.sleep(1)
        
        record_prompt = "Recording now..."
        eel_show_info(record_prompt)
        speak(record_prompt)
        
        try:
            recording = sounddevice.rec(int(DURATION_PER_SAMPLE * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sounddevice.wait()
            wav.write(filename, SAMPLE_RATE, recording)
            save_message = f"Sample {sample_num} saved."
            eel_show_info(save_message)
            speak(save_message)
            print(f"Saved {filename}")
        except Exception as e:
            error_message = f"An error occurred during recording or saving sample {sample_num}: {e}"
            eel_show_info(error_message)
            speak(error_message)
            print(error_message)
            return False

        if i < NUM_SAMPLES_REQUIRED - 1:
            time.sleep(1)

    success_message = f"Successfully collected {NUM_SAMPLES_REQUIRED} voice samples."
    eel_show_info(success_message)
    speak(success_message)
    print(success_message)
    return True

if __name__ == '__main__':
    print("Running voice enrollment script directly for testing...")
    # This is a placeholder for potential path adjustments if needed for direct testing:
    # import sys
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.join(current_dir, '..', '..') 
    # sys.path.append(project_root)
    # try:
    #   from backend.command import speak 
    #   print("Successfully imported backend.command.speak for testing.")
    # except ImportError as e:
    #   print(f"Could not import backend.command.speak for testing: {e}. Mock will be used.")
    
    if collect_voice_samples():
        print("Voice enrollment test completed successfully.")
    else:
        print("Voice enrollment test failed.")
