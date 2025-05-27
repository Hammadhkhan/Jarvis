import time
import datetime
import pyttsx3
import speech_recognition as sr
import eel

# Import functions from backend.feature
from backend.feature import openCommand, findContact, whatsApp, PlayYoutube, chatBot

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
        # For text input, we might want to speak the query for consistency, or not.
        # For now, let's assume text inputs don't need to be spoken back immediately.
        # If it's a command, the command handler will speak. If it's for chatbot, chatbot response will be spoken.

    try:
        command_executed = False
        for keyword, function in command_mapping.items():
            if keyword in query:
                function(query) # These functions handle their own speak() calls
                command_executed = True
                # For specific commands, we generally don't want to add them to chatbot history
                # unless the command itself is a form of conversation (e.g., setting a reminder).
                # For now, only chatbot interactions update conversation_log.
                break  

        if not command_executed:
            # This is where the chatbot logic is invoked
            # The original "I understood: {query}. Handing over to chatbot." is removed
            # as the chatbot's response will be the primary feedback.
            
            # Pass the current query and the conversation history
            assistant_response = chatBot(query, conversation_history=conversation_log)
            
            # Speak the assistant's response
            speak(assistant_response) # Crucial: speak the chatbot's actual reply

            # Update conversation history
            if query: # Ensure query is not None or empty before adding
                conversation_log.append({"role": "user", "content": query})
            if assistant_response: # Ensure response is not None or empty
                conversation_log.append({"role": "assistant", "content": assistant_response})

            # Keep conversation history to a manageable size
            if len(conversation_log) > MAX_HISTORY_MESSAGES:
                # Remove the oldest messages (e.g., the first two, which is one user/assistant pair)
                # This keeps the most recent N messages.
                conversation_log = conversation_log[len(conversation_log) - MAX_HISTORY_MESSAGES:]
                print(f"Conversation log trimmed to the last {MAX_HISTORY_MESSAGES} messages.")
            
            print(f"DEBUG: Current conversation log: {conversation_log}") # For debugging

    except Exception as e:
        print(f"An error occurred in takeAllCommands: {e}")
        speak("Sorry, something went wrong while processing your command.")
    
    eel.ShowHood()
