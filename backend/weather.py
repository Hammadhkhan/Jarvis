# backend/weather.py
import os
import requests # For making HTTP requests
import json   # For parsing JSON responses (though requests.json() handles it directly)
import time # For the test block

# Import the function to get the API key
try:
    from backend.api_service import get_openweathermap_api_key
except ImportError:
    # This mock is for making the script runnable for basic syntax checks if api_service is not yet available
    # or if there's a circular dependency during isolated testing.
    # In a real run invoked from main.py, api_service should be available.
    print("Warning: backend.api_service.get_openweathermap_api_key not found, using mock.")
    def get_openweathermap_api_key():
        print("Mock: get_openweathermap_api_key() called. Returning None or a dummy key for isolated testing.")
        # For direct testing of this script, you might want to hardcode a key here temporarily,
        # or ensure your env var / config.json is set up and api_service.py is in PYTHONPATH.
        # return "YOUR_DUMMY_KEY_FOR_TESTING_WEATHER_PY_STANDALONE" 
        return os.environ.get("OPENWEATHERMAP_API_KEY") # Still try env var

OPENWEATHERMAP_API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city_name: str) -> str:
    """
    Fetches current weather data for a given city from OpenWeatherMap API.

    Args:
        city_name (str): The name of the city.

    Returns:
        str: A human-readable weather forecast or an error message.
    """
    api_key = get_openweathermap_api_key()
    if not api_key:
        return "OpenWeatherMap API key is not configured. Please set it up."

    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # For temperature in Celsius
    }

    try:
        response = requests.get(OPENWEATHERMAP_API_BASE_URL, params=params, timeout=10) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        data = response.json()

        # Extracting relevant information
        weather_description = data.get("weather", [{}])[0].get("description", "not available").capitalize()
        temp = data.get("main", {}).get("temp", "N/A")
        feels_like = data.get("main", {}).get("feels_like", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A") # in m/s by default with metric units
        
        # City name from response can be more accurate if user input was ambiguous
        resolved_city_name = data.get("name", city_name)

        forecast = (
            f"Currently in {resolved_city_name}: {weather_description}. "
            f"The temperature is {temp}°C, but it feels like {feels_like}°C. "
            f"Humidity is at {humidity}%, and the wind speed is {wind_speed} meters per second."
        )
        return forecast

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return "Error: Invalid OpenWeatherMap API key. Please check your configuration."
        elif response.status_code == 404:
            return f"Error: Could not find weather data for city '{city_name}'. Please check the city name."
        else:
            return f"Error: HTTP error occurred while fetching weather: {http_err} (Status code: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the weather service. Please check your internet connection."
    except requests.exceptions.Timeout:
        return "Error: The request to the weather service timed out."
    except requests.exceptions.RequestException as req_err: # Catch any other requests error
        return f"Error: An unexpected error occurred with the weather service request: {req_err}"
    except KeyError as key_err: # If expected keys are missing in JSON
        # It's good to know what data looked like if a KeyError occurs
        # print(f"KeyError parsing weather data: {key_err} - Data received: {data}") # Avoid printing raw data in prod
        print(f"KeyError parsing weather data: {key_err}")
        return "Error: Received incomplete weather data from the service."
    except Exception as e: # Catch-all for any other unexpected error
        print(f"Unexpected error in get_weather: {e}")
        return "Sorry, an unexpected error occurred while fetching the weather."

if __name__ == '__main__':
    print("Testing Weather Module...")
    # To test, ensure OPENWEATHERMAP_API_KEY is set in env, or backend/config.json is configured
    # and backend.api_service can be imported correctly (check PYTHONPATH if needed).
    
    # Test cities
    cities = ["London", "Paris", "New York", "Tokyo", "InvalidCityName123"]
    
    # Example of how you might temporarily set up a config for testing if needed:
    # config_exists_for_test = os.path.exists("backend/config.json")
    # if not get_openweathermap_api_key() and not config_exists_for_test:
    #     if not os.path.exists("backend"): 
    #         try:
    #             os.makedirs("backend")
    #         except OSError as e:
    #             print(f"Could not create backend dir for dummy config: {e}")

    #     if os.path.exists("backend"): # Check if backend dir creation was successful
    #         try:
    #             with open("backend/config.json", "w") as f:
    #                 # IMPORTANT: Replace with a REAL key for actual testing, then REMOVE.
    #                 # DO NOT COMMIT A REAL KEY.
    #                 json.dump({"OPENWEATHERMAP_API_KEY": "YOUR_DUMMY_TEST_KEY_HERE"}, f) 
    #             print("INFO: Created dummy backend/config.json for testing. REMEMBER TO REMOVE OR USE ENV VAR.")
    #             print("INFO: For this test to work, ensure 'YOUR_DUMMY_TEST_KEY_HERE' is a valid key or use an env var.")
    #         except IOError as e:
    #             print(f"Could not write dummy config for testing: {e}")


    for city in cities:
        print(f"--- Weather for {city} ---")
        forecast_result = get_weather(city)
        print(forecast_result)
        print("-" * 30)
        # time.sleep(1) # Avoid hitting API rate limits if any during rapid tests; OpenWeatherMap free tier is quite generous.

    # Clean up dummy config if created by this test block (be careful with this logic)
    # A more robust way is to check if the key was specifically the dummy key.
    # if not config_exists_for_test and os.path.exists("backend/config.json"):
    #     try:
    #         with open("backend/config.json", "r") as f_read:
    #             temp_config_data = json.load(f_read)
    #         if temp_config_data.get("OPENWEATHERMAP_API_KEY") == "YOUR_DUMMY_TEST_KEY_HERE":
    #             # os.remove("backend/config.json")
    #             print("INFO: Remember to remove dummy backend/config.json if you created it for testing with a dummy key.")
    #     except Exception as e:
    #         print(f"Error during dummy config cleanup check: {e}")
            
    print("Weather module test complete (actual API calls made if key was available).")
