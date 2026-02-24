import os
import asyncio
import random
import logging
from flask import Flask, request, jsonify
from telethon import TelegramClient, events
import google.generativeai as genai
import sys

# ====== FLASK APP ======
app = Flask(__name__)

# ====== TERI VALUES ======
API_ID = 35049466
API_HASH = "9c6714cd19ba664355809d672e94d9b4"
PHONE_NUMBER = "+918920017674"
GEMINI_API_KEY = "AIzaSyAv93BloYUt0c9YYxEiiqLgnAUapM_ui8M"
# =========================

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Telegram client
client = TelegramClient('session_render', API_ID, API_HASH)

logging.basicConfig(level=logging.INFO)

# ====== GAALI LIST ======
gaali_list = ['bc', 'mc', 'bhosdike', 'madarchod', 'behenchod', 'gandu', 'chutiye', 'sale']

# ====== SOLUTIONS ======
solutions = {
    "net": "Airplane mode on-off kar.",
    "wifi": "Router restart kar.",
    "phone": "Phone restart kar.",
    "slow": "Cache clear kar.",
    "girlfriend": "Pehle maafi maang.",
}

# ====== DEFAULT REPLIES ======
default_replies = ["bhai busy hu", "thoda kaam me hu", "baad me batata hu"]

# ====== HEALTH CHECK ======
@app.route('/', methods=['GET'])
def health():
    return "Bot is running!", 200

# ====== MESSAGE HANDLER ======
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return
        
    msg = event.message.text
    sender = await event.get_sender()
    name = sender.first_name or "bhai"
    
    # Khud ka message ignore
    if hasattr(sender, 'phone') and sender.phone:
        if PHONE_NUMBER.replace("+", "") in sender.phone:
            return
    
    print(f"📨 {name}: {msg}")
    
    # Check gaali
    if any(g in msg.lower() for g in gaali_list):
        reply = random.choice(["apni maa ko samjha", "nikal yahan se", "bewakoof mat ban"])
    else:
        # Check solution
        reply = None
        for key, sol in solutions.items():
            if key in msg.lower():
                reply = sol
                break
        if not reply:
            reply = random.choice(default_replies)
    
    await asyncio.sleep(2)
    await event.reply(reply)
    print(f"🤖 Reply: {reply}")

async def start_bot():
    print("🔄 Connecting...")
    await client.start(phone=PHONE_NUMBER)
    print("✅ Bot Started!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    from threading import Thread
    
    def run_flask():
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)
    
    Thread(target=run_flask).start()
    
    print("🚀 Starting...")
    try:
        client.loop.run_until_complete(start_bot())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
