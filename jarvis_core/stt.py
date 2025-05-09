import speech_recognition as sr

recognizer  = None

def init_stt():
    global recognizer
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("STT: Calibrating for ambient noise, please wait...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("STT: Calibration complete.")
        except Exception as e:
            print(f"STT Error during calibration: {e}")

def listen_for_command():
    global recognizer
    if not recognizer:
        print("STT recognizer not initialized. Call init_stt() first.")
        return None

    with sr.Microphone() as source:
        print("\nListening for your command...")
        try:
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("STT: No speech detected within timeout.")
            return None
        except Exception as e:
            print(f"STT Error during listening: {e}")
            return None

    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("STT: Sorry, I did not understand that.")
        return None
    except sr.RequestError as e:
        print(f"STT: Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"STT Error during recognition: {e}")
        return None

init_stt()

if __name__ == '__main__':
    speak_direct = True  # Set to False if you don't have TTS from this file
    if speak_direct:
        try:
            from tts import speak as speak_tts
            speak_tts("Please say something to test the speech recognition.")
        except ImportError:
            print("Please say something to test the speech recognition (TTS module not found for prompt).")

    command = listen_for_command()
    if command:
        response = f"I heard you say: {command}"
        print(response)
        if speak_direct:
            try:
                from tts import speak as speak_tts
                speak_tts(response)
            except ImportError:
                pass  # TTS not available for this direct test
    else:
        msg = "No command was recognized."
        print(msg)
        if speak_direct:
            try:
                from tts import speak as speak_tts
                speak_tts(msg)
            except ImportError:
                pass