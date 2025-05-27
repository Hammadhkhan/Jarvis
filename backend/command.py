import time
import datetime
# import pyttsx3 # Removed pyttsx3
import speech_recognition as sr
import eel

# New imports for gTTS
from gtts import gTTS
import pygame # For playing audio
import os
import tempfile

# Import functions from backend.feature
from backend.feature import openCommand, findContact, whatsApp, PlayYoutube, chatBot
# Import for weather
from backend.weather import get_weather

# Initialize Conversation History
conversation_log = []
MAX_HISTORY_MESSAGES = 10 # Max messages (e.g., 5 user + 5 assistant pairs)

# Define Temporary Directory for TTS audio files
TEMP_TTS_DIR = "backend/temp_tts_audio/" 

# New speak function using gTTS
def speak(text):
    if not text: # Handle empty string case
        print("Speak function called with empty text.")
        return

    # Ensure temp directory exists
    os.makedirs(TEMP_TTS_DIR, exist_ok=True)

    # Ensure pygame.mixer is initialized
    # It's good practice to initialize it once, e.g., in main.py or at start of app.
    # feature.py also initializes it. Calling init() multiple times is safe for pygame.mixer.
    if not pygame.mixer.get_init():
         pygame.mixer.init()
         # print("Pygame mixer initialized in speak().") # Optional: for debugging

    temp_file_path = None # Initialize to ensure it's defined for finally block
    try:
        tts = gTTS(text=str(text), lang='en', slow=False)
        
        # Use tempfile to create a uniquely named temporary file
        fd, temp_file_path = tempfile.mkstemp(suffix=".mp3", dir=TEMP_TTS_DIR, prefix="tts_")
        os.close(fd) # Close the file descriptor, gTTS will open the path

        tts.save(temp_file_path)
        
        # Update UI after starting playback - this is more responsive
        # This assumes eel is available and connected
        if eel and getattr(eel, '_eel_current_url', None):
            eel.DisplayMessage(str(text)) 
            eel.receiverText(str(text)) 

        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) # Wait for speech to finish

    except gTTS.tts.gTTSError as gt_err: # Corrected exception class reference
        print(f"gTTS Error: {gt_err}. Text was: '{text}'")
        if eel and getattr(eel, '_eel_current_url', None):
            eel.DisplayMessage(f"Speech Error: Could not connect to TTS service. {gt_err}")
    except pygame.error as pg_err:
        print(f"Pygame Error: {pg_err}. Could not play audio for: '{text}'")
        if eel and getattr(eel, '_eel_current_url', None):
            eel.DisplayMessage(f"Speech Error: Could not play audio. {pg_err}")
    except Exception as e:
        print(f"Unexpected error in speak function: {e}. Text was: '{text}'")
        if eel and getattr(eel, '_eel_current_url', None):
            eel.DisplayMessage(f"Unexpected speech error for: '{text}'")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                # Ensure music is stopped before attempting to delete
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                     pygame.mixer.music.stop()
                
                os.remove(temp_file_path)
            except Exception as e_del:
                print(f"Error deleting temporary speech file {temp_file_path}: {e_del}")

# Preserved takecommand function (from Turn 39 content)
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 8)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        eel.DisplayMessage(query)
        speak(query) # Speak the user's recognized command
    except Exception as e:
        print(f"Error: {str(e)}\n")
        speak("Sorry, I could not understand. Please try again.")
        return None
    return query.lower()

# Preserved Wrapper functions (from Turn 39 content)
def open_command_wrapper(query):
    openCommand(query)

def handle_whatsapp_request(query):
    flag = ""
    if "send message" in query:
        flag = 'message'
    elif "call" in query:
        flag = 'call'
    elif "video call" in query:
        flag = 'video call'
    else:
        speak("Could not determine WhatsApp action. Please specify send message, call, or video call.")
        return

    Phone, name = findContact(query)
    if Phone and name: 
        if flag == 'message':
            speak(f"What message would you like to send to {name}?")
            message_content = takecommand()
            if message_content: 
                whatsApp(Phone, message_content, flag, name)
            else:
                speak(f"No message content provided for {name}. WhatsApp action cancelled.")
        else: 
            whatsApp(Phone, query, flag, name)
    else:
        print(f"Cannot proceed with WhatsApp action for '{query}' as contact was not found.")

def play_youtube_command(query):
    PlayYoutube(query)

def get_time_command(query):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    response = f"The current time is {current_time}"
    speak(response)

# Preserved Command mapping (from Turn 39 content)
command_mapping = {
    "open": open_command_wrapper,
    "send message": handle_whatsapp_request,
    "call": handle_whatsapp_request,
    "video call": handle_whatsapp_request,
    "on youtube": play_youtube_command,
    "time": get_time_command,
}

# Preserved takeAllCommands function (from Turn 39 content, with weather integration from Turn 35)
@eel.expose
def takeAllCommands(message=None):
    global conversation_log 

    if message is None:
        query = takecommand()
        if not query:
            eel.ShowHood()
            return
        print(f"Voice input: {query}")
        eel.senderText(query)
    else:
        query = message.lower()
        print(f"Message received: {query}")
        eel.senderText(query)

    try:
        command_executed = False
        for keyword, function in command_mapping.items():
            if keyword in query: 
                function(query) 
                command_executed = True
                break  
        
        if not command_executed:
            if "weather in" in query or "how's the weather in" in query or \
               "temperature in" in query or "forecast for" in query or \
               query.startswith("weather "): 
                city_name = ""
                if "weather in" in query: city_name = query.split("weather in", 1)[-1].strip()
                elif "how's the weather in" in query: city_name = query.split("how's the weather in", 1)[-1].strip()
                elif "temperature in" in query: city_name = query.split("temperature in", 1)[-1].strip()
                elif "forecast for" in query: city_name = query.split("forecast for", 1)[-1].strip()
                elif query.startswith("weather "):
                     parts = query.split("weather ", 1)
                     if len(parts) > 1: city_name = parts[1].strip()
                if city_name.endswith("?"): city_name = city_name[:-1].strip()

                if city_name:
                    weather_report = get_weather(city_name)
                    speak(weather_report)
                else:
                    speak("Which city's weather are you interested in? Please try again, for example, say 'weather in London'.")
                command_executed = True 
            else: 
                assistant_response = chatBot(query, conversation_history=conversation_log)
                speak(assistant_response)
                if query: conversation_log.append({"role": "user", "content": query})
                if assistant_response: conversation_log.append({"role": "assistant", "content": assistant_response})
                if len(conversation_log) > MAX_HISTORY_MESSAGES:
                    conversation_log = conversation_log[len(conversation_log) - MAX_HISTORY_MESSAGES:]
                    print(f"Conversation log trimmed to the last {MAX_HISTORY_MESSAGES} messages.")
                print(f"DEBUG: Current conversation log: {conversation_log}")
    except Exception as e:
        print(f"An error occurred in takeAllCommands: {e}")
        speak("Sorry, something went wrong while processing your command.")
    eel.ShowHood()
