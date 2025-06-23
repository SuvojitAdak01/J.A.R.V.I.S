from jarvis_core.ml.intent_classifier import IntentClassifier

if __name__ == '__main__':
    # Path of training data
    training_data_path = 'config/training_data.json'
    # Path where the trained model will be saved
    model_save_path = 'jarvis_core/ml/model'

    classifier = IntentClassifier()
    classifier.train(training_data_path)

    classifier.save_model(model_save_path)

    print("\n--- Testing Model ---")
    tests = [
        "Hey Jarvis",
        "what's the time",
        "weather in Mumbai",
        "open up my calculator",
        "who is shah rukh khan",
        "5 times 10",
        "turn the sound down",
        "that's all for now Jarvis"
    ]
    for test in tests:
        intent = classifier.predict(test)
        print(f"'{test}' -> Predicted Intent: '{intent}'")