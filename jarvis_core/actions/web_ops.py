import requests
import  wikipediaapi
from jarvis_core.utils import config_loader
from datetime import datetime, timezone

api_keys = config_loader.load_api_keys()
openweathermap_key = api_keys.get('openweathermap_api_key')

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="VoiceAssistant/v1.0",
    extract_format = wikipediaapi.ExtractFormat.WIKI
)

def kelvin_to_cel_fahren(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

def get_weather_action(location, unit_preference="celsius"):
    if not location:
        return "I need a location to check the weather! For example, What's the weather in London?"

    if not openweathermap_key or openweathermap_key == "YOUR_OPENWEATHERMAP_API_KEY_HERE":
        return "OpenWeatherMap API key is not configured. Please set it in config/api_keys.json."

    api_units = "metric"
    unit_symbol = "°C"
    if unit_preference.lower() == "fahrenheit":
        api_units = "imperial"
        unit_symbol = "°F"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}+&appid={openweathermap_key}&q={location}&units={api_units}"

    try:
        response = requests.get(complete_url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()

        if data.get("cod") != 200:
            error_msg = data.get("message", "Unknown error from weather API")
            return f"Sorry, I couldn't retrieve the weather for {location}. API Error: {error_msg}"

        main = data.get("main", {})
        weather_list = data.get("weather", [])
        weather_desc = weather_list[0].get("description", "not available") if weather_list else "not available"
        temp = main.get("temp", "N/A")
        feels_like = main.get("feels_like", "N/A")
        humidity = main.get("humidity", "N/A")
        city_name = data.get("name", location)
        sun_info = data.get("sys", {})
        sunrise_timestamp = sun_info.get("sunrise")
        sunset_timestamp = sun_info.get("sunset")

        sunrise_time = datetime.fromtimestamp(sunrise_timestamp, tz=timezone.utc).strftime(
            '%Y-%m-%d %I:%M:%S%p') if sunrise_timestamp else "N/A"
        sunset_time = datetime.fromtimestamp(sunset_timestamp, tz=timezone.utc).strftime(
            '%Y-%m-%d %I:%M:%S%p') if sunset_timestamp else "N/A"

        return (f"Temperature in {city_name} is: {temp}{unit_symbol}\n"
                f"Temperature feels like: {feels_like}{unit_symbol}\n"
                f"Humidity is {humidity}%\n"
                f"General weather : {weather_desc}\n"
                f"Sun risen at {sunrise_time}\n"
                f"Sun will set at {sunset_time}")

    except requests.exceptions.RequestException as e:
        print(f"Weather API request error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred in get_weather_action: {e}")

def search_wikipedia_action(entities):
    """Searches Wikipedia for the given query entity and returns a summary."""
    query = entities.get('query')
    if not query:
        return "What would you like me to search on Wikipedia?"

    try:
        page = wiki.page(query)
        if not page.exists():
            return f"Sorry, I couldn't find a Wikipedia page for '{query}'."

        # Taking the first few sentences of the summary.
        # The summary from wikipedia-api might be long.
        summary_sentences = page.summary.split('. ')
        if len(summary_sentences) > 2:
            short_summary = ". ".join(summary_sentences[:2]) + "."
        else:
            short_summary = page.summary

        if not short_summary: # If summary is empty even if page exists
             return f"I found a page for '{query}' but it doesn't have a readily available summary."

        return f"According to Wikipedia, regarding '{query}': {short_summary}"
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return f"Sorry, an error occurred while searching Wikipedia for '{query}'."

if __name__ == '__main__':
    #Testing weather
    if openweathermap_key and openweathermap_key != "YOUR_OPENWEATHERMAP_API_KEY_HERE":
        print("Testing Weather:")
        weather_result_london = get_weather_action(location='London', unit_preference='fahrenheit')
        print(f"London Weather:\n{weather_result_london}\n{'=' * 40}")
        weather_result_kolkata = get_weather_action(location='Kolkata', unit_preference='celsius')
        print(f"Kolkata Weather:\n{weather_result_kolkata}\n{'=' * 40}")
        weather_result_mumbai = get_weather_action(location='Mumbai', unit_preference='celsius')
        print(f"Mumbai Weather:\n{weather_result_mumbai}\n{'=' * 40}")
        weather_result_invalid = get_weather_action({'location': 'InvalidCityName123'})
        print(f"Invalid City Weather:\n{weather_result_invalid}\n{'=' * 40}")
        weather_no_location = get_weather_action({})
        print(f"No Location Weather:\n{weather_no_location}\n{'=' * 40}")

    # Test Wikipedia
    print("\nTesting Wikipedia:")
    wiki_python = search_wikipedia_action({'query': 'Python programming language'})
    print(f"Python Programming: {wiki_python}")
    wiki_mars = search_wikipedia_action({'query': 'Mars'})
    print(f"Mars: {wiki_mars}")
    wiki_nonexistent = search_wikipedia_action({'query': 'FlibbertygibbetXYZ'})
    print(f"Nonexistent Page: {wiki_nonexistent}")
    wiki_no_query = search_wikipedia_action({})
    print(f"No Query Wiki: {wiki_no_query}")