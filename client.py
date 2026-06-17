import os
from dotenv import load_dotenv
from openai import OpenAI

# Loads variables from a local .env file (see .env.example).
# .env is gitignored, so your real key never gets committed.
load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise SystemExit(
        "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
    )

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a virtual assistant named Nova skilled in general tasks like Alexa and Google Cloud"},
        {"role": "user", "content": "what is coding"},
    ],
)

print(completion.choices[0].message.content)
