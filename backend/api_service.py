# backend/api_service.py
import os
import json

CONFIG_FILE_PATH = "backend/config.json" # Updated path

def get_openai_api_key():
    """
    Retrieves the OpenAI API key.
    Prioritizes environment variable OPENAI_API_KEY.
    Falls back to reading from config.json if env var is not set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("Found OpenAI API key in environment variable.")
        return api_key

    # print(f"OpenAI API key not found in env var. Reading from {CONFIG_FILE_PATH}...") # Less verbose
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
            api_key = config.get("OPENAI_API_KEY")
            if api_key and api_key != "YOUR_OPENAI_API_KEY_HERE": # Check against placeholder
                # print(f"Found OpenAI API key in {CONFIG_FILE_PATH}.") # Less verbose
                return api_key
            # else: # Less verbose
                # print(f"OpenAI API key in {CONFIG_FILE_PATH} is missing or placeholder.")
        except Exception as e:
            print(f"Error reading OpenAI API key from {CONFIG_FILE_PATH}: {e}")
    # else: # Less verbose
        # print(f"Config file {CONFIG_FILE_PATH} not found for OpenAI key.")
    return None # Explicitly return None if not found or error

def get_openweathermap_api_key():
    """
    Retrieves the OpenWeatherMap API key.
    Prioritizes environment variable OPENWEATHERMAP_API_KEY.
    Falls back to reading from config.json if env var is not set.
    """
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if api_key:
        print("Found OpenWeatherMap API key in environment variable.")
        return api_key
    
    # print(f"OpenWeatherMap API key not found in env var. Reading from {CONFIG_FILE_PATH}...") # Less verbose
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
            api_key = config.get("OPENWEATHERMAP_API_KEY")
            if api_key and api_key != "YOUR_OPENWEATHERMAP_API_KEY_HERE": # Check against placeholder
                # print(f"Found OpenWeatherMap API key in {CONFIG_FILE_PATH}.") # Less verbose
                return api_key
            # else: # Less verbose
                # print(f"OpenWeatherMap API key in {CONFIG_FILE_PATH} is missing or placeholder.")
        except Exception as e:
            print(f"Error reading OpenWeatherMap API key from {CONFIG_FILE_PATH}: {e}")
    # else: # Less verbose
        # print(f"Config file {CONFIG_FILE_PATH} not found for OpenWeatherMap key.")
    return None # Explicitly return None if not found or error

if __name__ == '__main__':
    print("Testing API key retrieval functions...")
    
    openai_key = get_openai_api_key()
    if openai_key:
        print(f"OpenAI Key found (first 5 chars): {openai_key[:5]}...")
    else:
        print("OpenAI Key NOT found. Check env var OPENAI_API_KEY or backend/config.json.")

    openweathermap_key = get_openweathermap_api_key()
    if openweathermap_key:
        print(f"OpenWeatherMap Key found (first 5 chars): {openweathermap_key[:5]}...")
    else:
        print("OpenWeatherMap Key NOT found. Check env var OPENWEATHERMAP_API_KEY or backend/config.json.")
