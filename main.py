import requests
import json
import schedule
import time
import threading
from datetime import date
from telegram import Update
from telegram.ext import Application, PollAnswerHandler, CallbackContext

# Bot Credentials
TOKEN = "7226367133:AAHGaTSV-Z-baKL7weT2rvbi694nrp9UzGM"
CHAT_ID = "-4634419776"

# Salah times (24-hour format)
SALAH_TIMES = {
    "Fajr": "15:44",
    "Dhuhr": "15:45",
    "Asr": "15:46",
    "Maghrib": "15:47",
    "Isha": "15:48"
}

poll_tracking = {}
# Initialize bot application
app = Application.builder().token(TOKEN).build()

# Function to send a poll
def send_poll(prayer_name):
    question = f"Did you pray {prayer_name} today?"
    options = ["Yes", "No"]
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendPoll"
    payload = {
        "chat_id": CHAT_ID,
        "question": question,
        "options": json.dumps(options),  # Convert list to JSON format
        "is_anonymous": False
    }
    response = requests.post(url, data=payload)
    poll_data = response.json()

    if poll_data.get("ok"):
        print(f"✅ Poll for {prayer_name} sent successfully!")
    else:
        print(f"❌ Failed to send poll for {prayer_name}:", poll_data)

# Handle poll responses
async def poll_answer(update: Update, context: CallbackContext,):
    poll_id = update.poll_answer.poll_id
    user_id = update.poll_answer.user.id
    option_id = update.poll_answer.option_ids[0]  # Index of the selected option
    response_text = ["Yes", "No"][option_id]

    salah_name = poll_tracking.get(poll_id, "Unknown")

    response_data = {
        "user_id": user_id,
        "date": str(date.today()),
        "response": response_text,
        "prayer_name": salah_name
    }

    with open("responses.json", "a") as file:
        json.dump(response_data, file)
        file.write("\n")  # New line for each response

    print(f"📌 User {user_id} selected: {response_text}")

# Schedule the Salah polls
for prayer, salah_time in SALAH_TIMES.items():
    schedule.every().day.at(salah_time).do(send_poll, prayer)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 30 seconds

# Function to run the bot
def run_bot():
    app.add_handler(PollAnswerHandler(poll_answer))
    print("🤖 Bot is running and waiting for responses...")
    app.run_polling()

# Run both bot and scheduler in separate threads
if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    run_bot()  # This runs the Telegram bot continuously
