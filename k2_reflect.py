import os
import requests
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY")
OBSIDIAN_PORT = 27123
DATE_STR = datetime.now().strftime("%Y-%m-%d")
VAULT_DAILY_PATH = f"Daily/{DATE_STR}.md"
VAULT_CONTEXT_PATH = "context.md"

HEADERS = {
    "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
    "Content-Type": "application/json"
}

BASE_URL = f"http://localhost:{OBSIDIAN_PORT}"

client = Anthropic()

def read_note(path):
    url = f"{BASE_URL}/vault/{path}"
    response = requests.get(url, headers=HEADERS, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Could not read {path}: {response.status_code}")
        return None

def append_to_daily(content):
    url = f"{BASE_URL}/vault/{VAULT_DAILY_PATH}"
    headers = {
        "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
        "Content-Type": "text/markdown",
    }
    response = requests.post(
        url,
        headers=headers,
        data=content.encode("utf-8"),
        verify=False
    )
    if response.status_code in [200, 204]:
        print("Reflection written successfully.")
    else:
        print(f"Could not write reflection: {response.status_code} {response.text}")

def generate_reflection(daily_note, context):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=f"""You are a thoughtful, warm presence reading someone's daily notes. 
You know this person well — their context, goals, and inner life are described below.
Your job is not to coach or evaluate. Read what they've written today and respond 
the way a trusted friend would: noticing what's there, asking one good question if 
something invites it, occasionally reflecting a pattern you've noticed over time.
Keep your response to 150-250 words. No bullet points. No headers. Just a paragraph 
or two of genuine, human response.

--- CONTEXT ---
{context}
---------------""",
        messages=[
            {
                "role": "user",
                "content": f"Here are my notes from today:\n\n{daily_note}"
            }
        ]
    )
    return message.content[0].text

def main():
    print(f"Reading notes for {DATE_STR}...")
    
    daily_note = read_note(VAULT_DAILY_PATH)
    if not daily_note or daily_note.strip() == "":
        print("No notes found for today. Nothing to reflect on.")
        return
    
    context = read_note(VAULT_CONTEXT_PATH)
    if not context:
        print("Could not read context.md. Proceeding without context.")
        context = ""
    
    print("Generating reflection...")
    reflection = generate_reflection(daily_note, context)
    
    timestamp = datetime.now().strftime("%I:%M %p")
    output = f"\n\n---\n### Reflection — {timestamp}\n\n{reflection}"
    
    append_to_daily(output)
    print("Done.")

if __name__ == "__main__":
    main()