# J.A.R.V.I.S. - A Python-Powered Voice Assistant

![AI Assistant](https://img.shields.io/badge/AI-Assistant-blue.svg)
![Python Version](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)

A sophisticated, voice-controlled personal assistant built in Python. Inspired by the legendary AI from Iron Man, this project aims to create a modular and intelligent assistant that can understand natural language and perform a variety of tasks.

## 🌟 Features

J.A.R.V.I.S. is currently equipped with a Machine Learning-based intent classifier and can perform the following actions through voice commands:

* **Real-time Conversation:** Listens for commands and responds with voice, using offline Text-to-Speech.
* **Information Retrieval:**
    * Get the current time and date.
    * Fetch real-time weather information for any location (multi-turn conversation for preferences).
    * Search Wikipedia for information on people, places, and concepts.
* **System & Application Control:**
    * Open and close desktop applications (customizable via a config file).
    * Open websites and perform Google searches.
    * Control system volume (increase, decrease, set to a specific level, and mute/unmute).
* **Complex Calculations:**
    * Perform arithmetic operations (+, -, \*, /).
    * Handle trigonometric functions (sin, cos, tan), logarithms, powers, roots, and factorials.

## 🛠️ Getting Started

Follow these steps to get a copy of J.A.R.V.I.S. running on your local machine.

### Prerequisites

* **Python 3.11+**
* **Git** for cloning the repository.
* **Microphone** access for voice commands.
* **Internet Connection** for speech recognition (Google Web Speech API) and fetching web data.

### Setup and Installation

1.  **Clone the Repository**
    Open your terminal or command prompt and run:
    ```bash
    git clone https://github.com/SuvojitAdak01/J.A.R.V.I.S.git
    cd J.A.R.V.I.S
    ```

2.  **Create a Python Virtual Environment**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Install all the required Python libraries using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    This will install all the necessary packages. It will also download the `en_core_web_sm` model for spaCy.

4.  **Configure API Keys and Paths**
    Some features require configuration.

    * **(Required for Weather)** **OpenWeatherMap API Key:**
        1.  Sign up for a free account at [OpenWeatherMap](https://openweathermap.org/appid).
        2.  Create a file named `api_keys.json` inside the `config/` directory.
        3.  Add your key to the file like this:
            ```json
            {
              "openweathermap_api_key": "YOUR_API_KEY_HERE"
            }
            ```

    * **(Required for Opening Apps)** **Application Paths:**
        1.  Open the `config/app_paths.json` file.
        2.  Find the section for your operating system (`windows`, `macos`, or `linux`).
        3.  **Edit the paths** to match the locations of the applications on your computer.

### Training the AI Model

Before you can run JARVIS for the first time, you must train the intent classification model on your specific command patterns.

* **Customize Training Data (Optional but Recommended):**
    Open `config/training_data.json` and add or modify the phrases for each intent `tag` to make JARVIS better understand your way of speaking.

* **Run the Training Script:**
    Execute the following command in your terminal from the project's root directory:
    ```bash
    python train_model.py
    ```
    This will create/update the model files in `jarvis_core/ml/model/`. You only need to re-run this script when you make significant changes to `config/training_data.json`.

### Running J.A.R.V.I.S.

Once the setup and training are complete, you can start the assistant.

```bash
python main.py
```

JARVIS will initialize and greet you. It is now listening for your commands.

## 🚀 Usage

Here are some example commands you can give to JARVIS:

* **General:** `"Hello JARVIS"`, `"What time is it?"`, `"What's the date today?"`
* **Weather:** `"Tell me the weather in Mumbai"`
* **Wikipedia:** `"Who was Albert Einstein?"`, `"Tell me about the solar system"`
* **Calculations:** `"What is 50 times 12?"`, `"Calculate the square root of 144"`
* **Apps & Sites:** `"Open calculator"`, `"Launch Chrome"`, `"Close calculator"`
* **Volume:** `"Increase volume"`, `"Set the volume to 75 percent"`, `"Mute"`

---
