import os
import asyncio
import random
import logging
from flask import Flask, request, jsonify
from telethon import TelegramClient, events
import google.generativeai as genai

# ====== FLASK APP (YEH IMPORTANT HAI) ======
app = Flask(__name__)

# ====== TERI VALUES (BADAL MAT) ======
API_ID = 35049466
API_HASH = "9c6714cd19ba664355809d672e94d9b4"
PHONE_NUMBER = "+918920017674"
GEMINI_API_KEY = "AIzaSyAv93BloYUt0c9YYxEiiqLgnAUapM_ui8M"
# ====================================

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Telegram client
client = TelegramClient('session_render', API_ID, API_HASH)

# Logging
logging.basicConfig(level=logging.INFO)

# ====== GAALI LIST ======
gaali_list = ['bc', 'mc', 'bhosdike', 'madarchod', 'behenchod', 'gandu', 
              'chutiye', 'sale', 'harami', 'kutte', 'laude', 'gadhe']

# ====== SOLUTIONS ======
solutions = {
    "net": "Network problem? Airplane mode on-off kar, router restart kar.",
    "wifi": "Wifi nahi chal raha? Router band kar ke 10 second baad on kar.",
    "internet": "Internet slow hai? Data off-on kar, background apps band kar.",
    "phone": "Phone hang ho raha? Cache clear kar ya phone restart kar.",
    "slow": "Slow lag raha? Storage full hai kya? delete junk files.",
    "call": "Network problem hai, network change kar.",
    "app": "App crash ho raha? Reinstall kar le bhai.",
    "battery": "Battery fast drain? Dark mode use kar, background apps band kar.",
    "girlfriend": "Girlfriend se problem? Pehle maafi maang, fir chocolate de.",
    "friend": "Dost se fight? Ek baar call kar ke baat kar le.",
    "job": "Job nahi mil rahi? Naukri.com pe profile bana.",
    "paise": "Paisa problem? Expense track kar, extra income source dhundh.",
}

# ====== DEFAULT REPLIES ======
default_replies = [
    "bhai abhi busy hu thoda baad me baat karte hai",
    "bhai thoda kaam me hu, baad me batata hu",
    "dekh leta hu bhai abhi thoda time de",
    "ha bhai sun raha hu, thoda ruk",
]

# ====== CHECK GAALI ======
def is_gaali(text):
    text = text.lower()
    for g in gaali_list:
        if g in text:
            return True
    return False

# ====== FIND SOLUTION ======
def find_solution(text):
    text = text.lower()
    for key, sol in solutions.items():
        if key in text:
            return sol
    return None

# ====== AI RESPONSE ======
async def get_ai_response(user_message, sender_name):
    try:
        prompt = f"""Tu ek Indian ladka hai jo Hinglish mein baat karta hai. 
{sender_name} ne kaha: "{user_message}"
Rules:
- AGAR GALI DI: use gaali de
- AGAR PROBLEM PUCHI: solution de
- AGAR NORMAL: normal reply de
- Hinglish mein reply de"""
        
        response = model.generate_content(prompt)
        return response.text[:500]
    except Exception as e:
        logging.error(f"AI Error: {e}")
        solution = find_solution(user_message)
        if solution:
            return solution
        return random.choice(default_replies)

# ====== HEALTH CHECK ======
@app.route('/', methods=['GET'])
def health():
    return "Bot is running!", 200

# ====== WEBHOOK ======
@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "ok"}), 200

# ====== MESSAGE HANDLER ======
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handler(event):
    msg = event.message.text
    sender = await event.get_sender()
    name = sender.first_name or "bhai"
    
    # Khud ka message ignore
    if sender.phone and PHONE_NUMBER.replace("+", "") in sender.phone:
        return
    
    print(f"📨 From {name}: {msg}")
    
    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(random.randint(2, 4))
        reply = await get_ai_response(msg, name)
        await event.reply(reply)
        print(f"🤖 Reply: {reply}")

# ====== START BOT ======
async def start_bot():
    await client.start(phone=PHONE_NUMBER)
    print("✅ Bot Started!")
    await client.run_until_disconnected()

# ====== MAIN ======
def main():
    # Flask alag thread mein
    from threading import Thread
    def run_flask():
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port)
    
    Thread(target=run_flask).start()
    
    # Bot start
    print("🚀 Starting bot...")
    client.loop.run_until_complete(start_bot())

if __name__ == "__main__":
    main()
