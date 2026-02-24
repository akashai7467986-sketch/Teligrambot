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

# Telegram client with simpler settings
client = TelegramClient('session_render', API_ID, API_HASH)

# Logging
logging.basicConfig(level=logging.INFO)

# ====== GAALI LIST ======
gaali_list = ['bc', 'mc', 'bhosdike', 'madarchod', 'behenchod', 'gandu', 
              'chutiye', 'sale', 'harami', 'kutte', 'laude']

# ====== SOLUTIONS ======
solutions = {
    "net": "Network problem? Airplane mode on-off kar.",
    "wifi": "Router restart kar.",
    "phone": "Phone restart kar.",
    "slow": "Cache clear kar.",
    "girlfriend": "Pehle maafi maang.",
}

# ====== DEFAULT REPLIES ======
default_replies = [
    "bhai busy hu baad me baat karte hai",
    "thoda kaam me hu",
]

# ====== HEALTH CHECK ======
@app.route('/', methods=['GET'])
def health():
    return "Bot is running!", 200

# ====== WEBHOOK ======
@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "ok"}), 200

# ====== MESSAGE HANDLER ======
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # Sirf private messages handle karo
    if not event.is_private:
        return
        
    msg = event.message.text
    sender = await event.get_sender()
    name = sender.first_name or "bhai"
    
    # Khud ka message ignore
    if hasattr(sender, 'phone') and sender.phone and PHONE_NUMBER.replace("+", "") in sender.phone:
        return
    
    print(f"📨 From {name}: {msg}")
    
    # Check gaali
    is_gaali_msg = any(g in msg.lower() for g in gaali_list)
    
    # Simple reply (AI avoid kar rahe abhi error ke liye)
    if is_gaali_msg:
        reply = "apni maa ko samjha pehle"
    else:
        # Check solution
        solution = None
        for key, sol in solutions.items():
            if key in msg.lower():
                solution = sol
                break
        
        if solution:
            reply = solution
        else:
            reply = random.choice(default_replies)
    
    await asyncio.sleep(2)
    await event.reply(reply)
    print(f"🤖 Reply: {reply}")

# ====== START BOT ======
async def start_bot():
    print("🔄 Connecting to Telegram...")
    await client.start(phone=PHONE_NUMBER)
    print("✅ Bot Started Successfully!")
    await client.run_until_disconnected()

# ====== MAIN ======
if __name__ == "__main__":
    # Flask alag thread mein
    from threading import Thread
    
    def run_flask():
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)
    
    Thread(target=run_flask).start()
    
    # Bot start
    print("🚀 Starting bot...")
    
    try:
        client.loop.run_until_complete(start_bot())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
