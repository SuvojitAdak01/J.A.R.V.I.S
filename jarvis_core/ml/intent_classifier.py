import json
import joblib
import os
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder

class IntentClassifier:
    def __init__(self):
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        classifier = LogisticRegression(random_state=42, max_iter=200)
        self.pipeline = make_pipeline(vectorizer, classifier)
        self.label_encoder = LabelEncoder()
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def _preprocess(self, text):
        doc = self.nlp(text.lower())
        return " ".join([token.text for token in doc if not token.is_punct])

    def train(self, data_path):
        """Training the intent classifier model"""
        with open(data_path, 'r') as f:
            data = json.load(f)

        patterns = []
        tags = []
        for intent in data['intents']:
            for pattern in intent['patterns']:
                patterns.append(pattern)
                tags.append(intent['tag'])

        processed_patterns = [self._preprocess(p) for p in patterns]

        encoded_tags = self.label_encoder.fit_transform(tags)

        self.pipeline.fit(processed_patterns, encoded_tags)
        print("Training complete")

    def predict(self, text):
        """Predicting the intent of the given text"""
        processed_text = self._preprocess(text)
        prediction = self.pipeline.predict([processed_text])

        tag = self.label_encoder.inverse_transform(prediction)[0]
        return tag

    def save_model(self, model_path):
        """Saving the trained pipeline and label encoder."""
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        joblib.dump(self.pipeline, os.path.join(model_path, "intent_pipeline.joblib"))
        joblib.dump(self.label_encoder, os.path.join(model_path, "label_encoder.joblib"))
        print(f"Model saved to {model_path}")

    def load_model(self, model_path):
        """Loading a pre-trained model."""
        try:
            self.pipeline = joblib.load(os.path.join(model_path, "intent_pipeline.joblib"))
            self.label_encoder = joblib.load(os.path.join(model_path, "label_encoder.joblib"))
            print("Model loaded successfully.")
            return True
        except FileNotFoundError:
            print("Error: Model files not found. Please train the model first.")
            return False