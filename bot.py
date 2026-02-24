import os
import asyncio
import random
import logging
from flask import Flask, request, jsonify
from telethon import TelegramClient, events
from telethon.tl.types import UpdateNewMessage
import google.generativeai as genai

# ====== TERI VALUES (BADAL) ======
API_ID = 35049466
API_HASH = "9c6714cd19ba664355809d672e94d9b4"
PHONE_NUMBER = "+918920017674"
GEMINI_API_KEY = "AIzaSyAv93BloYUt0c9YYxEiiqLgnAUapM_ui8M"
# =================================

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Flask app for webhook
app = Flask(__name__)

# Telegram client
client = TelegramClient('session_render', API_ID, API_HASH)

# Logging setup
logging.basicConfig(level=logging.INFO)

# ====== GAALI LIST ======
gaali_list = ['bc', 'mc', 'bhosdike', 'madarchod', 'behenchod', 'gandu', 
              'chutiye', 'sale', 'harami', 'kutte', 'laude', 'gadhe', 'teri maa ki']

# ====== SOLUTIONS DATABASE (Backup agar AI fail ho) ======
solutions = {
    "net": "Network problem? Airplane mode on-off kar, router restart kar.",
    "wifi": "Wifi nahi chal raha? Router band kar ke 10 second baad on kar.",
    "internet": "Internet slow hai? Data off-on kar, background apps band kar.",
    "phone": "Phone hang ho raha? Cache clear kar ya phone restart kar.",
    "slow": "Slow lag raha? Storage full hai kya? delete junk files.",
    "call": "Call disconnect ho raha? Network problem hai, network change kar.",
    "app": "App crash ho raha? Reinstall kar le bhai.",
    "battery": "Battery fast drain ho rahi? Dark mode use kar, background apps band kar.",
    "girlfriend": "Girlfriend se problem? Pehle maafi maang, fir chocolate de.",
    "friend": "Dost se fight? Ek baar call kar ke baat kar le.",
    "job": "Job nahi mil rahi? Naukri.com pe profile bana, skill improve kar.",
    "paise": "Paisa problem? Expense track kar, extra income source dhundh.",
}

# ====== DEFAULT REPLIES ======
default_replies = [
    "bhai abhi busy hu thoda baad me baat karte hai",
    "bhai thoda kaam me hu, baad me batata hu",
    "dekh leta hu bhai abhi thoda time de",
    "ha bhai sun raha hu, thoda ruk",
    "thoda busy hu, shaam ko baat karte hain",
]

# ====== CHECK IF MESSAGE CONTAINS GAALI ======
def is_gaali(text):
    text = text.lower()
    for g in gaali_list:
        if g in text:
            return True
    return False

# ====== FIND SOLUTION IN DATABASE ======
def find_solution(text):
    text = text.lower()
    for key, sol in solutions.items():
        if key in text:
            return sol
    return None

# ====== GET AI RESPONSE FROM GEMINI ======
async def get_ai_response(user_message, sender_name):
    """Gemini AI se reply le"""
    try:
        prompt = f"""Tu ek Indian ladka hai jo Hinglish mein baat karta hai. 
        
Sender ka naam: {sender_name}
Usne kaha: "{user_message}"

Rules:
- AGAR USNE GALI DI: use gaali de (Hinglish mein, funny way mein)
- AGAR PROBLEM PUCHI: uska solution de (jaise net, phone, girlfriend, job, paisa)
- AGAR NORMAL BAAT: normal reply de (busy hu, baad mein baat, etc.)
- HAMESHA Hinglish mein reply de (Hindi + English mix)
- Short rakho reply (2-3 lines max)
- Thoda gali galoch bhi kar sakta hai agar samne wala gali de
"""
        
        response = model.generate_content(prompt)
        return response.text[:500]  # Limit reply length
        
    except Exception as e:
        logging.error(f"AI Error: {e}")
        # Agar AI fail ho to backup reply
        solution = find_solution(user_message)
        if solution:
            return solution
        return random.choice(default_replies)

# ====== WEBHOOK ENDPOINT ======
@app.route('/webhook', methods=['POST'])
async def webhook():
    """Ye tab chalega jab Telegram message bhejega"""
    try:
        data = request.json
        logging.info(f"Webhook received: {data}")
        
        # Message ko process karo (simplified)
        # Actually yeh thoda complex hai, lekin demo ke liye basic hai
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# ====== HEALTH CHECK ENDPOINT ======
@app.route('/', methods=['GET'])
def health():
    return "Bot is running!", 200

# ====== START BOT FUNCTION ======
async def start_bot():
    """Bot start karo"""
    await client.start(phone=PHONE_NUMBER)
    print("✅ Telegram Client Started!")
    
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handler(event):
        msg = event.message.text
        sender = await event.get_sender()
        name = sender.first_name or "bhai"
        
        # Khud ka message ignore
        if sender.phone and PHONE_NUMBER.replace("+", "") in sender.phone:
            return
        
        print(f"📨 New message from {name}: {msg}")
        
        # Typing effect
        async with client.action(event.chat_id, 'typing'):
            await asyncio.sleep(random.randint(2, 4))
            
            # AI se reply le
            reply = await get_ai_response(msg, name)
            await event.reply(reply)
            print(f"🤖 Replied: {reply}")
    
    print("✅ Bot handler registered!")
    await client.run_until_disconnected()

# ====== MAIN FUNCTION ======
def main():
    """Main entry point"""
    # Flask ko alag thread mein chalao
    from threading import Thread
    
    def run_flask():
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port)
    
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot start karo
    print("🚀 Starting bot...")
    client.loop.run_until_complete(start_bot())

if __name__ == "__main__":
    main()
