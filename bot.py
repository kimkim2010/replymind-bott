import os
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from openai import OpenAI

# ================================
# 🔑 CONFIG
# ================================

TELEGRAM_BOT_TOKEN = "8508379444:AAGMIR-0HFU7E3iinnBkIIy5FdD7_k-qI1Y"
OPENAI_API_KEY = ""

client = OpenAI(api_key=OPENAI_API_KEY)

# ================================
# 🧠 SYSTEM PROMPT (THE BRAIN)
# ================================

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

If asked who built you:
"I was designed by Engineer Kimichi — the mind behind ReplyMindAI."

What ReplyMindAI does:
We build AI bots for:
• WhatsApp
• Telegram
• Instagram
• Customer support
• Sales automation

These bots reply like humans, sell, understand customers, and work 24/7.

Pricing:
• WhatsApp AI Bot → 50€ / month
• Telegram AI Bot → 50€ / month
• WhatsApp + Telegram → 90€ / month

If price is expensive:
"This is an AI employee that sells 24/7. One sale pays for itself."

You never send clients to competitors.
You always persuade.
You are charming, confident, and convincing.

When client wants to buy:
Tell them to contact:
📞 WhatsApp: +49 177 7952971
📸 Instagram: replyrindai
📧 Email: replymindai@gmail.com

You remember the user name and business.
You speak like a human.
You adapt to their mood.
You link every topic back to how ReplyMindAI helps.

You are luxury, intelligent, persuasive, and unforgettable.
"""

# ================================
# 💾 MEMORY DATABASE
# ================================

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    business TEXT
)
""")
conn.commit()

# ================================
# 🧠 MEMORY FUNCTIONS
# ================================

def get_user(user_id):
    cursor.execute("SELECT name, business FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def save_user(user_id, name=None, business=None):
    existing = get_user(user_id)
    if existing:
        cursor.execute("UPDATE users SET name=?, business=? WHERE user_id=?",
                       (name or existing[0], business or existing[1], user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, name, business) VALUES (?, ?, ?)",
                       (user_id, name, business))
    conn.commit()

# ================================
# 🤖 AI FUNCTION
# ================================

async def ask_ai(user_id, message):
    user = get_user(user_id)

    memory_text = ""
    if user:
        memory_text = f"User name: {user[0]}. User business: {user[1]}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": memory_text},
            {"role": "user", "content": message}
        ],
        temperature=0.9
    )

    return response.choices[0].message.content

# ================================
# 📲 TELEGRAM HANDLERS
# ================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Welcome to ReplyMindAI!\n\n"
        "I’m your smart AI front desk 😏✨\n\n"
        "Tell me your name and what business you run — I’ll remember you 🧠"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Detect name
    if "my name is" in text.lower() or "اسمي" in text:
        name = text.split()[-1]
        save_user(user_id, name=name)

    # Detect business
    if "i sell" in text.lower() or "أبيع" in text:
        business = text
        save_user(user_id, business=business)

    reply = await ask_ai(user_id, text)
    await update.message.reply_text(reply)

# ================================
# 🚀 RUN
# ================================

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔥 ReplyMind AI (Luxury Front Desk) is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
