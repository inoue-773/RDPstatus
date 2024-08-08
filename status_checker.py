import schedule
import time
import subprocess
import requests
import re

# Your Discord webhook URL
DISCORD_WEBHOOK_URL = input("enter your webhook URL... ")
# Target account name to check for RDP sessions
TARGET_ACCOUNT = input("enter your server account name...") 


already_sent = False
previous_state = None

def check_rdp_sessions():
    """Executes qwinsta, prints output, analyzes results for the target account, and sends a Discord embed ONLY if the state has changed."""

    global already_sent, previous_state

    try:
        result = subprocess.run("qwinsta", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Error running qwinsta: {result.stderr}")

        # Print the qwinsta command output to the console
        print("---- qwinsta Output ----")
        print(result.stdout)
        print("------------------------")

        is_occupied = False
        for line in result.stdout.splitlines():
            if TARGET_ACCOUNT in line:
                if "Active" in line:
                    is_occupied = True
                break

        # Check if the state has changed
        if is_occupied != previous_state:
            already_sent = False 

        # Only send a message if the state has changed and it hasn't been sent yet
        if not already_sent:
            embed = {
                "title": "🖥️RDP Session Status",
                "description": f"This is the RDP status of {TARGET_ACCOUNT}",
                "fields": [
                    {
                        "name": "Status", 
                        "value": "⛔Occupied" if is_occupied else "✔️Not Occupied", 
                        "inline": True 
                    }
                ],
                "color": 0xe74c3c if is_occupied else 0x2ecc71,
                "footer": {
                    "text": "RDP Status by NickyBoy", 
                    "icon_url": "https://i.imgur.com/0egmGkf.png"
                }
            }

            payload = {"embeds": [embed]}
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

            if response.status_code != 204:
                print(f"Failed to send message to Discord: {response.status_code}")

            already_sent = True  
            previous_state = is_occupied 

    except Exception as e:
        print(f"An error occurred: {e}")

# Schedule the task to run every 20 seconds
schedule.every(20).seconds.do(check_rdp_sessions)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
