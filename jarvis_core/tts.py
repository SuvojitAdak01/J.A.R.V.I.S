import pyttsx3

engine  = None

def init_tts():
    global engine
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice' , voices[3].id)
        # engine.setProperty('rate', 210)
    except Exception as e:
        print(f"Error Initializing TTS engine: {e}")
        engine = None

def speak(text):
    global engine
    if not engine:
        print("TTS engine not initialized. Call init_tts() first")
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error during speech: {e}")

init_tts()

if __name__ == "__main__":
    speak("Hello, this is a test of the text to speech system")
    speak("JARVIS version 2.0 online. How can I help you ?")