import spacy
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def _parse_math_query(text):
    replacements = {
        # Powers & Roots (most specific first)
        r"the (\d+)(?:st|nd|rd|th) root of": r"nth_root(",  # e.g., the 4th root of
        r"cube root of": "cbrt(",
        r"square root of": "sqrt(",
        # Logarithms
        r"natural log of": "ln(",
        r"log of": "log10(",  # Default log to base 10
        # Trigonometry (with degrees handling)
        r"(?:sine|sin) of": "sin(radians(",
        r"(?:cosine|cos) of": "cos(radians(",
        r"(?:tangent|tan) of": "tan(radians(",
        r"(?:arcsine|inverse sine|asin) of": "degrees(asin(",
        r"(?:arccosine|inverse cosine|acos) of": "degrees(acos(",
        r"(?:arctangent|inverse tangent|atan) of": "degrees(atan(",
        # Other functions
        r"factorial of": "factorial(",
        # Basic arithmetic (words to symbols)
        r" plus ": " + ",
        r" minus ": " - ",
        r" times ": " * ",
        r" x ": " * ",
        r" multiplied by ": " * ",
        r" divided by ": " / ",
        r" modulus ": " % ",
        r" modulo ": " % ",
        # Powers (words to symbols)
        r" to the power of ": "**",
        r" squared": "**2",
        r" cubed": "**3",
        # Constants
        r"\bpi\b": "pi",
        r"\be\b": "e",
    }

    processed_text = text.lower()

    processed_text = re.sub(r'([\d\.]+) factorial', r'factorial(\1)', processed_text)

    #Handling phrases like "log base 2 of 8"
    log_base_match = re.search(r"log base ([\d\.]+) of ([\d\.]+)", processed_text)
    if log_base_match:
        base, number = log_base_match.groups()
        processed_text = processed_text.replace(log_base_match.group(0), f"log({number}, {base})")

    #Handling phrases like "the 4th root of 81"
    nth_root_match = re.search(r"the ([\d\.]+)(?:st|nd|rd|th) root of ([\d\.]+)", processed_text)
    if nth_root_match:
        root, number = nth_root_match.groups()
        processed_text = processed_text.replace(nth_root_match.group(0), f"nth_root({number}, {root})")

    for pattern, replacement in replacements.items():
        processed_text = re.sub(pattern, replacement, processed_text)

    processed_text = processed_text.replace(" degrees", ")")

    open_paren = processed_text.count('(')
    close_paren = processed_text.count(')')
    if open_paren > close_paren:
        processed_text += ')' * (open_paren - close_paren)

    # Clean up: remove words that are not part of the expression
    # Words like "what", "is", "calculate", "compute", "tell", "me", "the"
    cleanup_words = ["what's", "what is", "whats", "calculate", "compute", "the result of", "tell me", "of", "how much is"]
    for word in cleanup_words:
        processed_text = processed_text.replace(word, "")

    final_expression = re.sub(r"[^a-z0-9\s\.\+\-\*\/\%\(\)\,]", "", processed_text).strip()

    return final_expression

def process_text(text):
    """
        Processes text to extract intent and entities.
        For now, we'll use rule-based intent recognition.
        Returns a dictionary like: {'intent': 'some_intent', 'entities': {'entity_name': 'value'}}
    """

    doc = nlp(text.lower())
    intent = None
    entities = {}

    calculation_triggers = ["calculate", "compute", "what is", "what's", "result of"]
    has_number = any(token.like_num for token in doc)
    mathy_words = ["plus", "minus", "times", "divided", "root", "power", "log", "sin", "cos", "tan", "factorial"]
    mathy_symbols = ['+', '-', '*', '/', 'x']

    has_mathy_word = any(token.lemma_ in mathy_words for token in doc)
    has_mathy_symbol = any(symbol in text for symbol in mathy_symbols)
    has_trigger_phrase = any(trigger in text.lower() for trigger in calculation_triggers)

    if (has_trigger_phrase and has_number) or (has_number and (has_mathy_word or has_mathy_symbol)):
        if "time" not in text.lower() and "date" not in text.lower() and "weather" not in text.lower():
            intent = "calculate"
            entities['expression'] = _parse_math_query(text)
            return {'intent':intent, 'entities': entities}

    if any(token.lemma_ in ["hello", "hi", "hey", "greetings"] for token in doc):
        intent = "greet"
    elif (any(token.lemma_ in ["what", "tell"] for token in doc) and
          any(token.lemma_ == "time" for token in doc) and
          not any(token.lemma_ == "date" for token in doc)):  # Avoid confusion with date
        intent = "get_time"
    elif (any(token.lemma_ in ["what", "tell"] for token in doc) and
          any(token.lemma_ == "date" for token in doc)):
        intent = "get_date"
    elif any(token.lemma_ in ["goodbye", "bye", "exit", "quit", "terminate"] for token in doc):
        intent = "exit"
    elif any(token.lemma_ == "weather" for token in doc):
        intent = "get_weather"
        # Basic entity extraction for location (looks for proper nouns, especially GPE - Geopolitical Entity)
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity (cities, countries)
                entities['location'] = ent.text
                break
        if not entities.get('location'):
            # Fallback: if no GPE, look for nouns after "in", "for", "of" near "weather"
            for token in doc:
                if token.lemma_ == "weather":
                    # Check tokens after "weather in/for/of LOCATION"
                    children = [child for child in token.children if child.dep_ in ("prep", "pobj")]
                    for child_prep in children:  # e.g. "in"
                        for child_loc in child_prep.children:  # e.g. "london"
                            if child_loc.pos_ == "PROPN" or child_loc.pos_ == "NOUN":
                                entities['location'] = child_loc.text
                                break
                        if entities.get('location'): break
                    if not entities.get('location') and token.i + 2 < len(doc) and doc[token.i + 1].lemma_ in ["in",
                                                                                                               "for",
                                                                                                               "of"]:
                        entities['location'] = doc[token.i + 2].text
    elif (any(token.lemma_ in ["search", "wikipedia", "who is", "what is", "tell me about"] for token in doc) and
          not any(token.lemma_ == "weather" for token in doc)):  # Avoid clash with weather
        intent = "search_wikipedia"
        # Extract the search query (rudimentary: take text after the trigger phrase)
        # A more robust way would be to identify the main noun phrase.
        trigger_phrases = ["search wikipedia for", "wikipedia", "search for", "who is", "what is", "tell me about"]
        query_parts = []
        text_to_search = text.lower()
        found_trigger = False
        for phrase in trigger_phrases:
            if phrase in text_to_search:
                # Take the part after the phrase
                query_parts = text_to_search.split(phrase, 1)[-1].strip().split()
                found_trigger = True
                break
        if not found_trigger:  # if no specific trigger, take significant nouns/proper nouns
            query_parts = [token.text for token in doc if
                           token.pos_ in ["PROPN", "NOUN", "ADJ"] and token.lemma_ not in ["search", "wikipedia",
                                                                                           "tell", "me", "about"]]

        if query_parts:
            entities['query'] = " ".join(query_parts)
        elif len(doc) > 2:  # Fallback if specific triggers aren't clear
            entities['query'] = " ".join([token.text for token in doc[2:]])

    if not intent and len(doc) > 0:  # If no specific intent was matched
        intent = "unknown"  # Default fallback intent

    print(f" Text='{text}', Intent='{intent}', Entities='{entities}'")  # Debug print
    return {'intent': intent, 'entities': entities}

if __name__ == "__main__":
    tests = [
        "Hello JARVIS",
        "what is the time?",
        "tell me the current date",
        "what's the weather like in London",
        "weather in Mumbai please",
        "search Wikipedia for Python programming",
        "who is Albert Einstein",
        "tell me about the Eiffel Tower",
        "goodbye",
        "this is some random unrecognized command"
    ]

    for test_txt in tests:
        result = process_text(test_txt)
        print(f"Input: '{test_txt}' -> Intent: {result['intent']}, Entities: {result['entities']}")

    result = process_text("what is the current weather for New Delhi")
    print(f"Input: 'what is the current weather for New Delhi' -> Intent: {result['intent']}, Entities: {result['entities']}")