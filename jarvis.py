import os
import datetime
import pyttsx3
import speech_recognition as sr
import pywhatkit
import wikipedia
import pyjokes
from dotenv import load_dotenv
from openai import OpenAI
from wikipedia.exceptions import DisambiguationError, PageError

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize TTS engine
engine = pyttsx3.init()
# Set voice by index
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Hazel (UK)


def talk(text):
    """Speak out the given text."""
    print(f"🧠 Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listen to user voice and convert it to text."""
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True 
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        voice = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(voice).lower()
            print(f"🗣️ You said: {command}")
            return command
        except sr.UnknownValueError:
            print("I didn’t catch that.")
            return ""
        except sr.RequestError as e:
            print("Speech recognition error:", e)
            return ""

def ask_gpt(prompt):
    """Send a prompt to ChatGPT and return the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error with GPT:", e)
        return "Sorry, I couldn't connect to ChatGPT."

def search_wikipedia(query):
    """Fetch a summary from Wikipedia and handle disambiguation errors."""
    try:
        return wikipedia.summary(query.strip(), sentences=1)
    except DisambiguationError as e:
        return f"'{query}' is ambiguous. Be more specific."
    except PageError:
        return f"Sorry, I couldn't find anything on '{query}'."

def run_jarvis():
    """Main command loop."""
    command = take_command()

    if "play" in command:
        song = command.replace("play", "").strip()
        talk(f"Playing {song}")
        pywhatkit.playonyt(song)

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        talk(f"It's {current_time}")

    elif "who is" in command:
        person = command.replace("who is", "").strip()
        info = search_wikipedia(person)
        talk(info)

    elif "joke" in command:
        joke = pyjokes.get_joke()
        talk(joke)

    elif "ask" in command:
        prompt = command.replace("ask", "").strip()
        answer = ask_gpt(prompt)
        talk(answer)

    elif "stop" in command:
        talk("Goodbye!")
        exit()

# Start the assistant
if __name__ == "__main__":
    while True:
        run_jarvis()
