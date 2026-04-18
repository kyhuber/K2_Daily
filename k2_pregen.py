"""
k2_pregen.py

Pre-creates the next 30 days of daily notes in Obsidian so they're
always available on your phone and Mac before you need them.

Run manually: python3 k2_pregen.py
Or schedule via launchd on the 1st of each month.
"""

import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

OBSIDIAN_API_KEY = os.environ.get("OBSIDIAN_API_KEY")

OBSIDIAN_PORT = 27123
BASE_URL = f"http://localhost:{OBSIDIAN_PORT}"
DAYS_AHEAD = 30

def note_exists(path):
    url = f"{BASE_URL}/vault/{path}"
    headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
    response = requests.get(url, headers=headers, verify=False)
    return response.status_code == 200

def create_note(path, content):
    url = f"{BASE_URL}/vault/{path}"
    headers = {
        "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
        "Content-Type": "text/markdown",
    }
    response = requests.put(
        url,
        headers=headers,
        data=content.encode("utf-8"),
        verify=False
    )
    return response.status_code in [200, 204]

def main():
    print(f"Pre-generating {DAYS_AHEAD} daily notes...\n")
    created = 0
    skipped = 0

    for i in range(DAYS_AHEAD):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        date_display = date.strftime("%A, %B %-d, %Y")
        path = f"Daily/{date_str}.md"
        template = f"# {date_display}\n\n"

        if note_exists(path):
            print(f"  exists:  {date_str}")
            skipped += 1
        else:
            success = create_note(path, template)
            if success:
                print(f"  created: {date_str}")
                created += 1
            else:
                print(f"  FAILED:  {date_str}")

    print(f"\nDone. {created} created, {skipped} already existed.")

if __name__ == "__main__":
    main()
