# backend/llm_service.py
import os
import json

CONFIG_FILE_PATH = "backend/config_openai.json"

def get_openai_api_key():
    """
    Retrieves the OpenAI API key.
    Prioritizes environment variable OPENAI_API_KEY.
    Falls back to reading from backend/config_openai.json if env var is not set.
    Returns the API key string or None if not found.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print("Found OpenAI API key in environment variable.")
        return api_key

    print(f"OpenAI API key not found in environment variable. Attempting to read from {CONFIG_FILE_PATH}...")
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
            api_key = config.get("OPENAI_API_KEY")
            if api_key and api_key != "YOUR_API_KEY_HERE":
                print(f"Found OpenAI API key in {CONFIG_FILE_PATH}.")
                return api_key
            else:
                print(f"API key in {CONFIG_FILE_PATH} is missing or is the placeholder value.")
                return None
        except Exception as e:
            print(f"Error reading API key from {CONFIG_FILE_PATH}: {e}")
            return None
    else:
        print(f"Config file {CONFIG_FILE_PATH} not found.")
        return None

if __name__ == '__main__':
    # Test the function
    key = get_openai_api_key()
    if key:
        print(f"Test: API Key successfully retrieved (first few chars): {key[:5]}...")
    else:
        print("Test: API Key not found. Ensure OPENAI_API_KEY env var is set or backend/config_openai.json contains a valid key.")
        print(f"To use the config file, create 'backend/config_openai.json' from the template and add your key.")
