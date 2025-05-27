import time
import datetime
import pyttsx3
import speech_recognition as sr
import eel

# Import functions from backend.feature
from backend.feature import openCommand, findContact, whatsApp, PlayYoutube, chatBot

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
        # speak(query) # Removed speak(query) from here as commands will be spoken by their handlers or if no command is found
    except Exception as e:
        print(f"Error: {str(e)}\n")
        speak("Sorry, I could not understand. Please try again.")
        return None
    return query.lower()

# Wrapper functions
def open_command_wrapper(query):
    openCommand(query)

def handle_whatsapp_request(query):
    flag = ""
    # Determine flag based on query
    if "send message" in query:
        flag = 'message'
        # It's important to get the message content *after* confirming the contact
    elif "call" in query:
        flag = 'call'
    elif "video call" in query:
        flag = 'video call'
    else:
        speak("Could not determine WhatsApp action. Please specify send message, call, or video call.")
        return

    Phone, name = findContact(query) # findContact might need to be adjusted or the query pre-processed to extract recipient
    if Phone != 0:
        if flag == 'message':
            speak(f"What message would you like to send to {name}?")
            message_content = takecommand()
            if message_content: # Ensure a message was actually captured
                whatsApp(Phone, message_content, flag, name)
            else:
                speak(f"No message content provided for {name}. WhatsApp action cancelled.")
        else: # For 'call' or 'video call'
            whatsApp(Phone, query, flag, name) # query might not be the right thing to pass for message content here
    else:
        speak(f"Could not find contact for {query}. WhatsApp action cancelled.")


def play_youtube_command(query):
    PlayYoutube(query)

def get_time_command(query):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    response = f"The current time is {current_time}"
    speak(response)

# Command mapping
command_mapping = {
    "open": open_command_wrapper,
    "send message": handle_whatsapp_request, # More specific than just "whatsapp"
    "call": handle_whatsapp_request,         # Route to the same handler
    "video call": handle_whatsapp_request,   # Route to the same handler
    "on youtube": play_youtube_command,
    "time": get_time_command,
}

@eel.expose
def takeAllCommands(message=None):
    if message is None:
        query = takecommand()
        if not query:
            # speak("No command was given or understood.") # takecommand now handles its own error speaking
            eel.ShowHood()
            return
        print(f"Voice input: {query}")
        eel.senderText(query)
        # speak(query) # Speak the recognized query before processing
    else:
        query = message.lower() # Ensure message is lowercased like takecommand output
        print(f"Message received: {query}")
        eel.senderText(query)
        # speak(f"Received command: {query}") # Optional: speak the command received via text input

    # Speak the recognized/received query once before processing
    # This was previously done in takecommand() or just after receiving a message
    # We should do it here to ensure it's spoken before any command action.
    # However, individual commands also call speak(), so this might be redundant or too chatty.
    # Let's comment it out for now and let command handlers do the speaking.
    # speak(query) 

    try:
        command_executed = False
        for keyword, function in command_mapping.items():
            if keyword in query:
                function(query)
                command_executed = True
                break  # Exit after the first matched command

        if not command_executed:
            # If no specific command was matched, treat it as a general query for the chatbot
            # Or speak that the command wasn't understood if not using a chatbot as a fallback.
            speak(f"I understood: {query}. Handing over to chatbot.") # Let user know what was understood
            chatBot(query)
            # speak("I'm not sure how to respond to that. Can you try a different command?")


    except Exception as e:
        print(f"An error occurred in takeAllCommands: {e}")
        speak("Sorry, something went wrong while processing your command.")
    
    eel.ShowHood()
