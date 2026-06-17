# Nova — Voice Assistant

A voice-activated desktop assistant that listens for the wake word "Nova," carries out everyday tasks, and falls back to an LLM (via Groq) for open-ended questions.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)

## Features

- **Wake-word activation** — say "Nova" to start listening, or speak a direct command
- **App launching** — open installed Windows applications by name, with fuzzy matching for near-misses
- **File & folder search** — locate and open files/folders across common user directories
- **Music search** — "play \<song\>" opens a YouTube Music search
- **Quick links** — open GitHub or LinkedIn profiles by voice
- **AI fallback** — anything else gets routed to an LLM (Groq's `llama-3.1-8b-instant`) for a spoken answer
- **Code-aware responses** — code is printed to the terminal instead of being read aloud
- **Text-to-speech** — responses are spoken back using Google TTS (`gTTS`) and played through `pygame`

## Prerequisites

- Python 3.9 or later
- A [Groq API key](https://console.groq.com) (free tier available)
- A working microphone
- Windows is recommended for full functionality (app-launching uses `os.startfile`); a Linux fallback exists for opening files but is untested on macOS

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create and activate a virtual environment** *(recommended)*
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > `PyAudio` occasionally needs a platform-specific install step:
   > - **Windows:** `pip install pyaudio` (or `pip install pipwin && pipwin install pyaudio` if that fails)
   > - **macOS:** `brew install portaudio && pip install pyaudio`
   > - **Linux:** `sudo apt-get install python3-pyaudio` (or build deps: `portaudio19-dev`)

4. **Configure your API key**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your real key:
   ```env
   GROQ_API_KEY=your_real_key_here
   ```
   `.env` is already listed in `.gitignore`, so it will never be committed.

## Usage

Run the assistant:
```bash
python nova.py
```

The first run calibrates your microphone for ambient noise (stay quiet for ~2 seconds), then waits for the wake word.

To sanity-check your API key without launching the full voice pipeline:
```bash
python client.py
```

## Voice Commands

| Say                                  | Action                                  |
|---------------------------------------|------------------------------------------|
| "Nova, open GitHub"                   | Opens the linked GitHub profile           |
| "Nova, open LinkedIn"                 | Opens the linked LinkedIn profile         |
| "Nova, open file \<name\>"            | Searches for and opens a file             |
| "Nova, open folder \<name\>"          | Searches for and opens a folder           |
| "Nova, open / launch / start \<app\>" | Opens an installed application            |
| "Nova, play \<song\>"                 | Searches the song on YouTube Music        |
| "Nova, who are you?"                  | Nova introduces itself and its creator    |
| Anything else                         | Routed to the AI for a spoken answer      |

## Project Structure

```
.
├── nova.py            # Main voice assistant — wake-word loop, command routing, TTS
├── client.py           # Minimal script to test that your Groq key works
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your local .env file
└── .gitignore           # Excludes .env, caches, and runtime files from git
```

## Security

Never commit a real API key. Always store secrets in a local `.env` file (gitignored) and keep `.env.example` as a placeholder only. If a key is ever accidentally exposed — committed, pasted, or shared — treat it as compromised and rotate it immediately at [console.groq.com](https://console.groq.com).

## Known Limitations

- `os.startfile` (used for opening apps/files) is Windows-only; the Linux `xdg-open` fallback is untested on macOS
- Speech recognition relies on Google's free Web Speech API, which requires an active internet connection
- Long AI responses are printed in full but only summarized verbally to avoid awkward text-to-speech of code or long passages

## Author

Built by **Jeet Makhija** — [github.com/jeet-43](https://github.com/jeet-43)
