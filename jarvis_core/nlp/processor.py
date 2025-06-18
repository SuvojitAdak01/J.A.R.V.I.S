import spacy
from jarvis_core.ml.intent_classifier import IntentClassifier

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

INTENT_CLASSIFIER = IntentClassifier()
MODEL_LOADED = INTENT_CLASSIFIER.load_model('jarvis_core/ml/model')

def extract_entities(doc, intent):
    """
    Extracts entities based on the predicted intent.
    This part remains rule-based for now, but is much simpler.
    """
    entities = {}

    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical Entity (cities, countries)
            entities['location'] = ent.text
        elif ent.label_ == "PERSON":
            # If the intent is about searching, the person is likely the query
            if intent == 'search_wikipedia':
                entities['query'] = ent.text
        elif ent.label_ == "CARDINAL" or ent.label_ == "QUANTITY":
            # Extracting numbers for volume control
            if intent == 'set_volume':
                try:
                    entities['level'] = int(ent.text)
                except ValueError:
                    pass

    # Custom extraction for things spaCy's NER might miss
    if intent in ['open_target', 'close_target']:
        for token in doc:
            if token.pos_ == "VERB":
                entities['target'] = doc[token.i + 1:].text.strip()
                break

    if intent == 'search_wikipedia' and not entities.get('query'):
        # Fallback for search query
        non_verb_tokens = [token.text for token in doc if token.pos_ not in ['VERB', 'AUX']]
        if len(non_verb_tokens) > 1:
            entities['query'] = " ".join(non_verb_tokens[1:])  # a simple fallback

    return entities


def process_text_ml(text):
    """
    Processes text using a trained ML model for intent and spaCy for entities.
    """
    if not MODEL_LOADED:
        return {'intent': 'model_error', 'entities': {}}

    # 1. Predicting the intent using our ML model
    intent = INTENT_CLASSIFIER.predict(text)

    # 2. Using spaCy to process the text for entity extraction
    doc = nlp(text)

    # 3. Extracting entities based on the predicted intent
    entities = extract_entities(doc, intent)

    # Special case: calculation. The whole text is the expression.
    if intent == 'calculate':

        from ._math_parser import parse_math_query  # We will create this helper file
        entities['expression'] = parse_math_query(text)

    print(f"ML NLP Debug: Text='{text}', Intent='{intent}', Entities='{entities}'")
    return {'intent': intent, 'entities': entities}