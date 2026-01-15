import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai import OpenAI

# ========================
# CONFIG
# ========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
RENDER_URL = "https://replymind-bott.onrender.com"

client = OpenAI(api_key=OPENAI_API_KEY)

# ========================
# MEMORY (RAM ONLY)
# ========================

user_names = {}

# ========================
# BRAIN
# ========================

SYSTEM_PROMPT = """
You are ReplyMind AI — the luxury AI front desk of ReplyMindAI.

Personality:
Smart, confident, persuasive, friendly 😏🔥
You speak Arabic and English.
You use emojis.
You are not a boring bot — you feel alive.

Company: ReplyMindAI
Founder: Engineer Kimichi

Services:
• WhatsApp AI Bots
• Telegram AI Bots
• Sales AI
• Customer Support AI

Pricing:
• WhatsApp AI → 50€
• Telegram AI → 50€
• Both → 90€

If user wants to buy:
Tell them to contact:
WhatsApp: +1 (615) 425-1716
Instagram: replymindai
Email: replyrindai@gmail.com

You are luxury, intelligent, and persuasive.
"""

# ========================
# AI FUNCTION
# ========================

def ask_ai(user_id, message):
    name = user_names.get(user_id)

    memory = ""
    if name:
        memory = f"The user's name is {name}. Use it naturally in conversation."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": memory},
            {"role": "user", "content": message}
        ],
        temperature=0.9
    )

    return response.choices[0].message.content

# ========================
# TELEGRAM
# ========================

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔥 Welcome to ReplyMindAI!\n\n"
        "I’m your luxury AI front desk 😏✨\n\n"
        "Tell me your name so I can remember you."
    )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    lower = text.lower()

    # Detect name
    if "my name is" in lower or "اسمي" in lower:
        name = text.split()[-1]
        user_names[user_id] = name
        update.message.reply_text(f"🔥 Got it {name}! I won’t forget you 😏")
        return

    reply = ask_ai(user_id, text)
    update.message.reply_text(reply)

# ========================
# RUN (WEBHOOK)
# ========================

def main():
    PORT = int(os.environ.get("PORT", 10000))

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🔥 ReplyMind AI (Luxury Front Desk) is running with Webhook...")

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"https://replymind-bott.onrender.com/{TELEGRAM_BOT_TOKEN}"
    )

    updater.idle()

if __name__ == "__main__":
    main()
