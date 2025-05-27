import time
import datetime
import pyttsx3
import speech_recognition as sr
import eel

# Import functions from backend.feature
from backend.feature import openCommand, findContact, whatsApp, PlayYoutube, chatBot
# New import for weather
from backend.weather import get_weather

# Initialize Conversation History
conversation_log = []
MAX_HISTORY_MESSAGES = 10 # Max messages (e.g., 5 user + 5 assistant pairs)

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[2].id)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 174)
    eel.receiverText(text)

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

# Wrapper functions (as they were in the original file)
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
    if Phone and name: # Check if Phone and name are not None/0/empty
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
        # findContact already speaks if contact not found, so just log or return
        print(f"Cannot proceed with WhatsApp action for '{query}' as contact was not found.")


def play_youtube_command(query):
    PlayYoutube(query)

def get_time_command(query):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    response = f"The current time is {current_time}"
    speak(response)

# Command mapping (as it was in the original file)
# Note: The new weather command will be handled by specific 'elif' conditions,
# not directly in this map, for more flexible phrase matching.
command_mapping = {
    "open": open_command_wrapper,
    "send message": handle_whatsapp_request,
    "call": handle_whatsapp_request,
    "video call": handle_whatsapp_request,
    "on youtube": play_youtube_command,
    "time": get_time_command,
}

@eel.expose
def takeAllCommands(message=None):
    global conversation_log # Declare intent to modify global variable

    if message is None:
        query = takecommand()
        if not query:
            eel.ShowHood()
            return
        print(f"Voice input: {query}")
        eel.senderText(query)
        # User's query is already spoken by takecommand()
    else:
        query = message.lower()
        print(f"Message received: {query}")
        eel.senderText(query)
        # For text input, we won't speak the query back immediately here.

    try:
        command_executed = False
        for keyword, function in command_mapping.items():
            if keyword in query: # Simple keyword check for mapped commands
                function(query) 
                command_executed = True
                break  
        
        if not command_executed:
            # Handle commands not in the simple map, like weather or fallback to chatbot
            if "weather in" in query or "how's the weather in" in query or \
               "temperature in" in query or "forecast for" in query or \
               query.startswith("weather "): # Catches "weather London"

                city_name = ""
                # Prioritize more specific phrases first
                if "weather in" in query:
                    city_name = query.split("weather in", 1)[-1].strip()
                elif "how's the weather in" in query:
                    city_name = query.split("how's the weather in", 1)[-1].strip()
                elif "temperature in" in query:
                    city_name = query.split("temperature in", 1)[-1].strip()
                elif "forecast for" in query:
                    city_name = query.split("forecast for", 1)[-1].strip()
                elif query.startswith("weather "): # Generic "weather cityname"
                     parts = query.split("weather ", 1)
                     if len(parts) > 1:
                         city_name = parts[1].strip()
                
                # Remove any potential question marks if city name is at the end
                if city_name.endswith("?"):
                    city_name = city_name[:-1].strip()

                if city_name:
                    # speak(f"Fetching weather for {city_name}...") # Optional intermediate feedback
                    weather_report = get_weather(city_name)
                    speak(weather_report)
                else:
                    speak("Which city's weather are you interested in? Please try again, for example, say 'weather in London'.")
                command_executed = True # Mark as executed even if city_name was missing, as intent was weather.

            else: # Fallback to chatbot if no other command matched
                assistant_response = chatBot(query, conversation_history=conversation_log)
                speak(assistant_response)

                if query: 
                    conversation_log.append({"role": "user", "content": query})
                if assistant_response: 
                    conversation_log.append({"role": "assistant", "content": assistant_response})

                if len(conversation_log) > MAX_HISTORY_MESSAGES:
                    conversation_log = conversation_log[len(conversation_log) - MAX_HISTORY_MESSAGES:]
                    print(f"Conversation log trimmed to the last {MAX_HISTORY_MESSAGES} messages.")
                
                print(f"DEBUG: Current conversation log: {conversation_log}")

    except Exception as e:
        print(f"An error occurred in takeAllCommands: {e}")
        speak("Sorry, something went wrong while processing your command.")
    
    eel.ShowHood()
