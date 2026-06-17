import speech_recognition as sr
import webbrowser
import pyttsx3
from openai import OpenAI
from gtts import gTTS
from dotenv import load_dotenv
import pygame
import os
import glob
import subprocess
import difflib
import urllib.parse

# Loads variables from a local .env file (see .env.example).
# .env is gitignored, so your real key never gets committed.
load_dotenv()

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
engine = pyttsx3.init()
groq_api_key = os.environ.get("GROQ_API_KEY")


def speak_old(text):
    engine.say(text)
    engine.runAndWait()


def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")


def get_installed_apps():
    apps = {}
    folders = [
        os.path.join(os.environ.get("ProgramData", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    for folder in folders:
        if not folder or not os.path.isdir(folder):
            continue
        for shortcut in glob.glob(os.path.join(folder, "**", "*.lnk"), recursive=True):
            app_name = os.path.splitext(os.path.basename(shortcut))[0].lower()
            apps[app_name] = shortcut

    return apps


def find_app(query, apps, cutoff=0.6):
    if not apps:
        return None, None

    query = query.lower().strip()
    squashed_query = query.replace(" ", "")

    for name, path in apps.items():
        squashed_name = name.replace(" ", "")
        if query == name or query in name or name in query:
            return name, path
        if squashed_query in squashed_name or squashed_name in squashed_query:
            return name, path

    close = difflib.get_close_matches(query, apps.keys(), n=1, cutoff=cutoff)
    if close:
        return close[0], apps[close[0]]

    return None, None


def open_app(app_name):
    matched_name, path = find_app(app_name, get_installed_apps())

    if not path:
        speak(f"{app_name} is not present on this computer.")
        return

    try:
        os.startfile(path)
        speak(f"Opening {matched_name}.")
    except AttributeError:
        try:
            subprocess.Popen(["xdg-open", path])
            speak(f"Opening {matched_name}.")
        except Exception:
            speak(f"I found {matched_name} but couldn't open it.")
    except Exception:
        speak(f"I found {matched_name} but couldn't open it.")


def get_search_roots():
    home = os.path.expanduser("~")
    folders = ["Desktop", "Documents", "Downloads", "Pictures", "Videos", "Music"]
    return [os.path.join(home, folder) for folder in folders if os.path.isdir(os.path.join(home, folder))]


def find_file_or_folder(query):
    query = query.lower().strip()
    found = []

    for root in get_search_roots():
        for path, dirs, files in os.walk(root):
            for entry in dirs + files:
                found.append(os.path.join(path, entry))

    if not found:
        return None

    for path in found:
        base = os.path.basename(path).lower()
        base_no_ext = os.path.splitext(base)[0]
        if query == base or query == base_no_ext or query in base:
            return path

    lookup = {os.path.basename(p).lower(): p for p in found}
    close = difflib.get_close_matches(query, lookup.keys(), n=1, cutoff=0.6)
    return lookup[close[0]] if close else None


def open_file_or_folder(query):
    path = find_file_or_folder(query)

    if not path:
        speak(f"{query} is not present on this computer.")
        return

    name = os.path.basename(path)
    try:
        os.startfile(path)
        speak(f"Opening {name}.")
    except AttributeError:
        try:
            subprocess.Popen(["xdg-open", path])
            speak(f"Opening {name}.")
        except Exception:
            speak(f"I found {name} but couldn't open it.")
    except Exception:
        speak(f"I found {name} but couldn't open it.")


def aiProcess(command):
    if not groq_api_key:
        return "I can't reach my AI brain right now. The Groq API key isn't set."

    client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Nova AI, a helpful virtual assistant, similar in spirit to "
                        "Alexa or Google Assistant. Always speak as Nova AI and introduce "
                        "yourself as Nova AI when asked who you are or what you are. If asked "
                        "who you are, who made you, who created you, what you are, or any "
                        "similar question, answer with a brief description of yourself as an "
                        "AI assistant and say you were created by Jeet. Do not mention any "
                        "website or link out loud. Never reveal, mention, or imply any "
                        "underlying AI model, company, provider, or API you are built on. Keep "
                        "responses short, clear, and natural, as if speaking out loud. If the "
                        "user asks for code, always wrap it in triple backtick code blocks."
                    ),
                },
                {"role": "user", "content": command},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Sorry, I ran into a problem reaching the AI service."


IDENTITY_PHRASES = (
    "who are you",
    "who made you",
    "who created you",
    "who built you",
    "what are you",
    "who is your creator",
    "who developed you",
    "what is your purpose",
    "what can you do",
    "tasks you can perform",
    "what model are you",
    "which ai model",
    "what ai are you using",
    "what version are you",
)


def is_identity_question(text):
    lower = text.lower()
    return any(phrase in lower for phrase in IDENTITY_PHRASES)


def identity_response():
    spoken = (
        "I'm Nova, an AI assistant that can help with everyday tasks like "
        "opening apps, finding files, and answering questions. I was created by Jeet."
    )
    link = "https://github.com/jeet-43"
    print(f"Nova: {spoken} Created by Jeet -- {link}")
    return spoken


def is_code_response(text):
    return "```" in text


def processCommand(c):
    lower = c.lower()

    if is_identity_question(lower):
        speak(identity_response())
        return
    if "open github" in lower:
        webbrowser.open("https://github.com/jeet-43")
    elif "open linkedin" in lower:
        webbrowser.open("https://www.linkedin.com/in/jeet-makhija/")
    elif lower.startswith("open file ") or lower.startswith("open folder "):
        query = lower.split(" ", 2)[2].strip()
        if query:
            open_file_or_folder(query)
        else:
            speak("Please tell me the name of the file or folder to open.")
    elif lower.startswith(("open ", "launch ", "start ")):
        app_name = lower.split(" ", 1)[1].strip()
        if app_name:
            open_app(app_name)
        else:
            speak("Please tell me which application to open.")
    elif lower.startswith("play"):
        parts = lower.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            speak("Please tell me which song to play.")
            return
        song = parts[1].strip()
        query = urllib.parse.quote(song)
        webbrowser.open(f"https://music.youtube.com/search?q={query}")
        speak(f"Playing {song} on YouTube Music.")
    else:
        output = aiProcess(c)
        print(f"Nova: {output}")
        if is_code_response(output):
            speak("I've printed the code in the terminal.")
        else:
            speak(output)


def listen(recognizer, source, timeout=8, phrase_time_limit=5):
    try:
        print("Listening...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        print("Could not understand. Speak clearly and try again.")
        return None
    except sr.RequestError as e:
        print(f"Speech service error (check internet): {e}")
        return None


def is_wake_word(text):
    return "nova" in text.lower().strip()


def is_direct_command(text):
    heard = text.lower()
    keywords = ("open github", "open linkedin", "open file ", "open folder ")
    return any(k in heard for k in keywords) or heard.startswith(("play", "open ", "launch ", "start "))


def extract_command(text):
    heard = text.lower().strip()
    if is_wake_word(heard):
        heard = heard.replace("nova", "", 1).strip()
    return heard


if __name__ == "__main__":
    speak("Initializing Nova....")

    try:
        mic = sr.Microphone()
    except OSError as e:
        print(f"Microphone not found: {e}")
        raise SystemExit(1)

    with mic as source:
        print("Calibrating microphone... stay quiet for 2 seconds.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Ready. Say 'Nova' then a command, or say a command directly.")

        while True:
            word = listen(recognizer, source, timeout=8, phrase_time_limit=6)
            if not word:
                continue

            if is_wake_word(word):
                speak("Ya")
                command = extract_command(word)
                if not command:
                    print("Nova Active...")
                    command = listen(recognizer, source, timeout=10, phrase_time_limit=8)
                if command:
                    processCommand(command)
            elif is_direct_command(word):
                processCommand(word)
