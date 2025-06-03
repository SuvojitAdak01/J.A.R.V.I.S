from http.client import responses

from jarvis_core import tts
from jarvis_core import stt
from jarvis_core.actions import system_ops
from jarvis_core.actions import web_ops
from jarvis_core.nlp import processor
from jarvis_core.nlp.processor import nlp as spacy_nlp_model

current_conversation_context = {}

def initiate_get_weather(entities):
    """
        Initiates the weather fetching process.
        If location is present, it asks for unit preference and sets conversation context.
    """
    global current_conversation_context
    location = entities.get('location')

    if not location:
        # Try to get location from a previous turn if context was about missing location for weather
        if current_conversation_context.get('original_intent') == 'get_weather' and \
                current_conversation_context.get('awaiting_input_for') == 'location':
            # This case would be if JARVIS previously asked "For which location?"
            # And the current command (now in 'entities' after NLP) *is* the location.
            # For simplicity, we'll assume 'location' is extracted by NLP if present.
            # If you want to handle "For which location?" -> "London" explicitly,
            # the NLP needs to identify that "London" is a location entity here.
            pass  # Let the 'if not location:' below handle it if still not found

    if not location:
        # If location is STILL not found by NLP from the current command
        current_conversation_context = {
            'awaiting_input_for': 'location',  # Now waiting for location
            'original_intent': 'get_weather'
        }
        return "For which location would you like the weather?"

        # Location is available, now ask for unit preference
    current_conversation_context = {
        'awaiting_input_for': 'weather_unit',
        'location': location,
        'original_intent': 'get_weather'
    }
    return "Do you prefer Celsius or Fahrenheit?"



action_handler = {
    "greet": lambda entities: "Hello Sir, How can I assist you today ?",
    "get_time": lambda entities: system_ops.get_current_time(),
    "get_date": lambda entities: system_ops.get_current_date(),
    "exit": lambda entities: "Goodbye Sir, Have a pleasant day!",
    "get_weather": initiate_get_weather, # Defined in web_ops.py
    "search_wikipedia": web_ops.search_wikipedia_action, # And this one too
    "unknown": lambda entities: "Sorry, I don't understand that command yet."
}

def handle_pending_conversation(command_text):
    """
    If a conversation is pending(e.g waiting for unit preference for temperature),
    this function tries to process command_text as the answer.
    """
    global current_conversation_context
    if not current_conversation_context:
        return None

    awaiting = current_conversation_context.get('awaiting_input_for')
    original_intent = current_conversation_context.get('original_intent')

    if original_intent == 'get_weather':
        if awaiting == 'weather_unit':
            unit_preference = None
            cmd_lower = command_text.lower()
            if "celsius" in cmd_lower or "metric" in cmd_lower or "c" == cmd_lower.strip() or "centigrade" in cmd_lower:
                unit_preference = "celsius"
            elif "fahrenheit" in cmd_lower or "imperial" in cmd_lower or "f" == cmd_lower.strip():
                unit_preference = "fahrenheit"

            if unit_preference:
                location = current_conversation_context.get('location')
                weather_report = web_ops.get_weather_action(location=location, unit_preference=unit_preference)
                current_conversation_context = {}  # Clear context, conversation resolved
                return weather_report
            else:
                # Didn't understand the unit preference, ask again or give up
                location = current_conversation_context.get('location')
                return f"Sorry, I didn't catch that. Please say Celsius or Fahrenheit."

        elif awaiting == 'location':  # If JARVIS asked "For which location?"
            # Directly process the input text with spaCy to find entities,
            # as the user likely just gave the location name in response.
            doc = spacy_nlp_model(command_text)  # Use the imported spaCy model directly
            location_entity = None
            print(f"DEBUG: Checking entities in '{command_text}' for pending location...")  # Debug
            for ent in doc.ents:
                print(f"DEBUG: Found entity: '{ent.text}' ({ent.label_})")  # Debug
                if ent.label_ == "GPE":  # Geopolitical Entity (cities, countries, states)
                    location_entity = ent.text
                    print(f"DEBUG: Identified GPE entity '{location_entity}'.")
                    break  # Take the first GPE found



            if not location_entity and len(doc) == 1 and doc[0].pos_ == "PROPN":
                location_entity = doc[0].text
                print(f"DEBUG: No GPE found, assuming single PROPN '{location_entity}' is location.")

            if location_entity:
                # Location found! Update context to wait for unit preference.
                current_conversation_context = {
                    'awaiting_input_for': 'weather_unit',
                    'location': location_entity,
                    'original_intent': 'get_weather'
                }
                # Ask the next question in the dialogue.
                response = f"Do you prefer Celsius or Fahrenheit for the weather?"
            else:

                print(f"DEBUG: No location entity (GPE or single PROPN) found in isolated response: '{command_text}'")

                response = "I still didn't quite catch the location. Could you please tell me the city name again?"


    return response

def process_command_nlp_v2(command_text):
    global current_conversation_context
    pending_response = handle_pending_conversation(command_text)

    if pending_response:
        return pending_response

    nlp_result = processor.process_text(command_text)
    intent = nlp_result.get('intent')
    entities = nlp_result.get('entities', {})

    if intent == "exit":
        response = action_handler[intent](entities)  # Get the goodbye message
        tts.speak(response)
        return "exit_signal"

    if intent in action_handler:
        action_function = action_handler[intent]
        # Passing entities; the handler function will use them or manage context
        return action_function(entities)

    else:
        return "I'm not sure how to handle that request right now."

def run_jarvis():
    tts.speak("JARVIS version 2.0 online. How can I help you ?")

    while True:
        command = stt.listen_for_command()

        if command:
            response = process_command_nlp_v2(command)
            if response == "exit_signal":
                break
            elif response:
                tts.speak(response)
            else:
                tts.speak("I didn't catch that, please try again!")

if __name__ == "__main__":
    run_jarvis()