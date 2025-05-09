from http.client import responses

from jarvis_core import tts
from jarvis_core import stt
from jarvis_core.actions import system_ops

def process_command(command):
    if command is None:
        return None
    response = None
    if "hello jarvis" in command or "hello" in command:
        response = "Hello Sir, How can I assist you today?"
    elif "time" in command:
        response = system_ops.get_current_time()
    elif "date" in command:
        response = system_ops.get_current_date()
    elif "goodbye" in command or "exit" in command or "quit" in command:
        response = "Goodbye Sir, Have a pleasant day!"
        tts.speak(response)
        return "exit"
    else:
        response = "Sorry, I don't understand that command yet."
    return response

def run_jarvis():
    tts.speak("JARVIS system online. How can I help you?")

    while True:
        command = stt.listen_for_command()

        if command:
            response = process_command(command)
            if response == "exit":
                break
            elif response:
                tts.speak(response)
            else:
                tts.speak("I didn't catch that, please try again!")

if __name__ == "__main__":
    run_jarvis()