# backend/feature.py

# Original imports (excluding hugchat)
from compileall import compile_path
import os
import re
from shlex import quote # Retained, used by whatsApp
import struct
import subprocess
import time
import webbrowser
import eel
# from hugchat import hugchat # REMOVED
import pvporcupine
import pyaudio
import pyautogui # Retained, used by hotword and whatsApp
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3

from backend.helper import extract_yt_term, remove_words

# New imports for OpenAI chatbot
from openai import OpenAI # Changed from "import openai" to "from openai import OpenAI" for OpenAI v1.x+
from backend.api_service import get_openai_api_key

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    # Ensure this path is correct for your environment or make it relative/configurable
    sound_file = r"C:\Users\patha\Videos\Jarvis\frontend\assets\audio\start_sound.mp3" 
    # Using a raw string or doubled backslashes for Windows paths
    # For better portability, consider relative paths if possible:
    # e.g., sound_file = os.path.join("frontend", "assets", "audio", "start_sound.mp3")
    # This would require main.py or run.py to be in the project root for this path to work.
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound {sound_file}: {e}")
        # speak("Error: Could not play assistant sound effect.") # Avoid speaking if speak itself is problematic or for minor errors

# Original openCommand function
def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query.lower()
    
    app_name = query.strip()

    if app_name != "":
        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])
                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak(f"Sorry, I could not find or open {app_name}.") # More informative
        except Exception as e: # Catch more specific exceptions if possible
            print(f"Error in openCommand: {e}")
            speak("Something went wrong while trying to open the application or website.")

# Original PlayYoutube function
def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

# Original hotword function
def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
        # Ensure correct access key and model path if not default
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        print("Hotword detection active...") # Added for clarity
        while True:
            keyword_data=audio_stream.read(porcupine.frame_length, exception_on_overflow=False) 
            keyword_unpacked=struct.unpack_from("h"*porcupine.frame_length,keyword_data)
            keyword_index=porcupine.process(keyword_unpacked)

            if keyword_index>=0:
                print(f"Hotword detected (index: {keyword_index})") # More informative
                pyautogui.keyDown("win")
                pyautogui.press("j")
                time.sleep(0.5) # Reduced sleep time
                pyautogui.keyUp("win")
                
    except pvporcupine.PorcupineActivationError as pae:
        print(f"Porcupine activation error: {pae}")
        # speak("There was an issue with the wake word detection service activation.") # Avoid speak in long-running background thread
    except pvporcupine.PorcupineError as pe:
        print(f"Porcupine error: {pe}")
        # speak("A wake word detection service error occurred.")
    except Exception as e:
        print(f"An unexpected error occurred in hotword detection: {e}")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()
        print("Hotword detection stopped.") # Added for clarity

# Original findContact function
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove) # Assuming remove_words is defined in backend.helper

    try:
        contact_name_query = query.strip().lower() # Use a different variable for clarity
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + contact_name_query + '%', contact_name_query + '%'))
        results = cursor.fetchall()
        if results:
            mobile_number_str = str(results[0][0])
            if not mobile_number_str.startswith('+91'): # Standardize number
                mobile_number_str = '+91' + mobile_number_str.lstrip('0') # Remove leading 0 if any
            return mobile_number_str, contact_name_query # Return the name used for lookup for clarity
        else:
            speak(f'Contact {contact_name_query} not found.')
            return None, None # Return None to indicate not found
    except Exception as e:
        print(f"Error in findContact: {e}")
        speak('An error occurred while searching for the contact.')
        return None, None
    
# Original whatsApp function
def whatsApp(Phone, message, flag, name): # 'name' here is the contact name from findContact
    if not Phone: # Check if Phone is None or empty
        speak(f"Cannot perform WhatsApp action for {name} due to missing phone number.")
        return

    if flag == 'message':
        target_tab = 12
        jarvis_message = "Message sent successfully to "+name
    elif flag == 'call':
        target_tab = 7
        message = '' 
        jarvis_message = "Calling to "+name
    else: # video call
        target_tab = 6
        message = '' 
        jarvis_message = "Starting video call with "+name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"' # For Windows

    try:
        # Using check=True will raise CalledProcessError if command fails
        subprocess.run(full_command, shell=True, check=True)
        time.sleep(5) 
        # The second run might be for focus or ensuring the message field is ready.
        # This part is platform-dependent and might need refinement.
        subprocess.run(full_command, shell=True, check=True) 
        
        # PyAutoGUI part is highly dependent on screen state and resolution.
        # Consider alternatives if this is unreliable.
        # pyautogui.hotkey('ctrl', 'f') # This might not be reliable
        time.sleep(1) # Give window time to activate
        for _ in range(target_tab): 
            pyautogui.hotkey('tab')
            time.sleep(0.1) # Small delay between tabs
        pyautogui.hotkey('enter')
        speak(jarvis_message)
    except subprocess.CalledProcessError as e:
        print(f"Error opening WhatsApp or sending command: {e}")
        speak(f"Sorry, I couldn't complete the WhatsApp action for {name}.")
    except Exception as e:
        print(f"Unexpected error in whatsApp: {e}")
        speak("An unexpected error occurred with WhatsApp.")

# New chatBot function using OpenAI
def chatBot(query, conversation_history=None):
    api_key = get_openai_api_key()
    if not api_key:
        # This message is returned to command.py, which will handle speaking it
        return "OpenAI API key is not configured. Please set it up to use the advanced chat features."

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return "Sorry, there was an issue initializing the smart chat service."

    messages = [{"role": "system", "content": "You are Jarvis, a helpful and concise AI assistant."}]
    
    if conversation_history: # Ensure history is in the correct format
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": query})

    try:
        # print(f"DEBUG: Sending to OpenAI: {messages}") # For debugging
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=150,
            n=1,
            stop=None
        )
        assistant_reply = completion.choices[0].message.content.strip()
        # The calling function in command.py will handle speak(assistant_reply)
        return assistant_reply
    except OpenAI.APIConnectionError as e: # Explicitly use OpenAI. for clarity
        print(f"OpenAI API Connection Error: {e}")
        return "Sorry, I couldn't connect to the OpenAI service. Please check your internet connection."
    except OpenAI.RateLimitError as e:
        print(f"OpenAI API Rate Limit Exceeded: {e}")
        return "Sorry, the smart chat service is experiencing high demand. Please try again later."
    except OpenAI.AuthenticationError as e:
        print(f"OpenAI API Authentication Error: {e}")
        return "OpenAI API authentication failed. Please check your API key."
    except OpenAI.APIError as e: 
        print(f"OpenAI API Error: {e}")
        return "Sorry, an unexpected error occurred with the smart chat service."
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred in chatBot: {e}")
        return "Sorry, I encountered an unexpected issue while trying to process your chat request."

# Standalone test block
if __name__ == '__main__':
    print("Testing new chatBot function (OpenAI)...")
    # Ensure OPENAI_API_KEY is set in env or backend/config_openai.json is configured
    
    # test_query = "Explain quantum physics in simple terms."
    # print(f"User: {test_query}")
    # response = chatBot(test_query) 
    # print(f"Jarvis (GPT): {response}")

    # test_history = [{"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "The capital of France is Paris."}]
    # test_query_with_history = "What is it famous for?"
    # print(f"User (with history): {test_query_with_history}")
    # response_with_history = chatBot(test_query_with_history, conversation_history=test_history)
    # print(f"Jarvis (GPT): {response_with_history}")
    
    print("Standalone chatBot test complete (actual calls commented out to prevent unintended API usage during subtask execution).")
    print("To perform a real test, uncomment the test calls and ensure API key is available.")
