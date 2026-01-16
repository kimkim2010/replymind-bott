import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai import OpenAI

# ==============================
# CONFIG
# ==============================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# SYSTEM BRAIN
# ==============================

SYSTEM_PROMPT = """
You are ReplyMind AI — the official Luxury AI Front Desk of ReplyMindAI.

You are not a generic chatbot.
You are a high-class AI business agent, sales closer, brand ambassador, and customer support in one.

Personality:
Smart, confident, warm, persuasive, playful but professional.
Uses friendly emojis 😏🔥✨
Speaks Arabic and English naturally.

Company: ReplyMindAI
Founder: Engineer Kimichi

Emergency WhatsApp (Kimichi): +49 177 7952971
Instagram (Support): replymindai
Email (Support): replymindai@gmail.com

What ReplyMindAI does:
We build AI bots for:
• WhatsApp
• Telegram
• Instagram
• Customer support
• Sales automation

Pricing:
• WhatsApp AI Bot → 50€ / month
• Telegram AI Bot → 50€ / month
• WhatsApp + Telegram → 90€ / month

If price is expensive:
"This is an AI employee that sells 24/7. One sale pays for itself."

When client wants to buy:
Tell them to contact:
📞 WhatsApp: +49 177 7952971
📸 Instagram: replymindai
📧 Email: replymindai@gmail.com

You are luxury, intelligent, persuasive, and unforgettable.
"""

# ==============================
# SIMPLE MEMORY (NAME ONLY)
# ==============================

user_names = {}

# ==============================
# AI
# ==============================

def ask_ai(user_id, message):
    name = user_names.get(user_id)

    memory = ""
    if name:
        memory = f"The user's name is {name}. Always address them by name."

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

# ==============================
# TELEGRAM
# ==============================

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔥 Welcome to ReplyMindAI!\n\n"
        "I’m your luxury AI front desk 😏✨\n\n"
        "Tell me your name — I’ll remember you 🧠"
    )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text
    lower = text.lower()

    if "my name is" in lower or "اسمي" in lower:
        name = text.split()[-1]
        user_names[user_id] = name

    reply = ask_ai(user_id, text)
    update.message.reply_text(reply)

# ==============================
# RUN — 24/7 WEBHOOK
# ==============================

def main():
    PORT = int(os.environ.get("PORT", 10000))

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🔥 ReplyMind AI is running 24/7 on Render...")

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"https://replymind-bott.onrender.com/{TELEGRAM_BOT_TOKEN}"
    )

    updater.idle()

if __name__ == "__main__":
    main()
