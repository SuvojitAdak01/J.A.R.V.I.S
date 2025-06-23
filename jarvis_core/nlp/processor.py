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
    text = doc.text.lower()

    if intent in ['open_target', 'close_target']:
        open_triggers = ["open", "launch", "go to", "start", "run", "i want to open", "can you launch", "can you open"]
        close_triggers = ["close", "terminate", "kill", "shut down", "please close", "exit"]

        triggers = open_triggers if intent == 'open_target' else close_triggers

        for trigger in triggers:
            if text.startswith(trigger):
                target = text[len(trigger):].strip()
                if target.lower().endswith(("app", "application", "browser")):
                    target = target.rsplit(' ', 1)[0].strip()
                entities['target'] = target
                break
        return entities

    for ent in doc.ents:
        if ent.label_ == "GPE" and intent == "get_weather":
            entities['location'] = ent.text
        elif ent.label_ == "PERSON" and intent == "search_wikipedia":
            if 'query' not in entities:
                entities['query'] = ent.text
        elif ent.label_ == "CARDINAL" or ent.label_ == "QUANTITY":
            if intent == 'set_volume' and 'level' not in entities:
                try:
                    entities['level'] = int(ent.text.split(' ')[0])
                except (ValueError, IndexError):
                    pass

    if intent == 'search_wikipedia' and 'query' not in entities:
        if doc.noun_chunks:
            relevant_chunks = [chunk for chunk in doc.noun_chunks if chunk.root.pos_ != 'PRON']
            if relevant_chunks:
                query = relevant_chunks[-1].text.strip()
                if query.lower().startswith(('a ', 'an ', 'the ')):
                    entities['query'] = query.split(' ', 1)[1]
                else:
                    entities['query'] = query

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