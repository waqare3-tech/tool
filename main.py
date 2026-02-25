import logging
import re
import sqlite3
import base64
import requests
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ===================== TOKEN =====================
TOKEN = "7787473053:AAFCg166nfOqQY6dJUJfQ3ct5Rfc66dxkrI"

# ===================== API URLs =====================
VEHICLE_API = "https://anupvehicleinfo07.vercel.app/lookup"
PHONE_API = "https://source-code-api.vercel.app/"
IP_API = "http://ip-api.com/json/"
BIN_API = "https://lookup.binlist.net/"

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== DATABASE =====================
def init_db():
    conn = sqlite3.connect('redx.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (user_id INTEGER PRIMARY KEY, 
                 username TEXT,
                 first_name TEXT,
                 join_date TEXT)''')
    conn.commit()
    conn.close()

# ===================== API FUNCTIONS =====================
def get_vehicle(rc):
    try:
        r = requests.get(f"{VEHICLE_API}?rc={rc}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_phone(phone):
    try:
        r = requests.get(f"{PHONE_API}?num={phone}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_ip(ip):
    try:
        r = requests.get(f"{IP_API}{ip}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_bin(bin_num):
    try:
        r = requests.get(f"{BIN_API}{bin_num}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# ===================== BOT COMMANDS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    conn = sqlite3.connect('redx.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?,?)",
              (user.id, user.username, user.first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    keyboard = [
        ['🚗 Vehicle Lookup', '📱 Phone Lookup'],
        ['🌍 IP Tracker', '💳 BIN Checker'],
        ['🔐 Password Check', '🔒 Encrypt'],
        ['📊 Stats', 'ℹ️ Help']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔥 RED-X MULTI TOOL BOT 🔥\n\nSelect option below 👇",
        reply_markup=reply_markup
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🤖 HELP MENU

/vehicle <rc>
/phone <number>
/ip <ip>
/bin <bin>
/password <pass>
/encrypt <text>
/decrypt <text>
/stats
""")

async def vehicle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /vehicle UP26R4007")

    rc = context.args[0].upper()
    data = get_vehicle(rc)

    if data:
        await update.message.reply_text(f"🚗 Vehicle Data:\n\n{data}")
    else:
        await update.message.reply_text("❌ No data found")

async def phone_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /phone 923001234567")

    phone = context.args[0]
    data = get_phone(phone)

    if data:
        await update.message.reply_text(f"📱 Phone Data:\n\n{data}")
    else:
        await update.message.reply_text("❌ No data found")

async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /ip 8.8.8.8")

    data = get_ip(context.args[0])
    if data:
        await update.message.reply_text(f"🌍 IP Info:\n\n{data}")
    else:
        await update.message.reply_text("❌ Invalid IP")

async def bin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /bin 411111")

    data = get_bin(context.args[0][:6])
    if data:
        await update.message.reply_text(f"💳 BIN Info:\n\n{data}")
    else:
        await update.message.reply_text("❌ BIN not found")

async def password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /password MyPass123!")

    pwd = " ".join(context.args)
    score = sum([
        len(pwd) >= 8,
        bool(re.search(r'[A-Z]', pwd)),
        bool(re.search(r'[a-z]', pwd)),
        bool(re.search(r'\d', pwd)),
        bool(re.search(r'[!@#$%^&*()]', pwd))
    ])

    strength = ["Weak", "Medium", "Strong", "Very Strong", "Ultra Strong"][score]

    await update.message.reply_text(f"🔐 Strength: {strength}")

async def encrypt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /encrypt hello")

    text = " ".join(context.args)
    enc = base64.b64encode(text.encode()).decode()
    await update.message.reply_text(f"🔒 Encrypted:\n{enc}")

async def decrypt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Example: /decrypt SGVsbG8=")

    try:
        dec = base64.b64decode(" ".join(context.args)).decode()
        await update.message.reply_text(f"🔓 Decrypted:\n{dec}")
    except:
        await update.message.reply_text("❌ Invalid encrypted text")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('redx.db')
    c = conn.cursor()
    c.execute("SELECT join_date FROM users WHERE user_id=?", (update.effective_user.id,))
    row = c.fetchone()
    conn.close()

    if row:
        await update.message.reply_text(f"📊 Joined:\n{row[0]}")
    else:
        await update.message.reply_text("❌ No stats")

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '🚗 Vehicle Lookup':
        await update.message.reply_text("Send RC number\nExample: UP26R4007")
    elif text == '📱 Phone Lookup':
        await update.message.reply_text("Send phone number\nExample: 923001234567")
    elif text == '🌍 IP Tracker':
        await update.message.reply_text("Send IP\nExample: 8.8.8.8")
    elif text == '💳 BIN Checker':
        await update.message.reply_text("Send BIN\nExample: 411111")
    elif text == '🔐 Password Check':
        await update.message.reply_text("Send password")
    elif text == '🔒 Encrypt':
        await update.message.reply_text("Send text to encrypt")
    elif text == '📊 Stats':
        await stats_cmd(update, context)
    elif text == 'ℹ️ Help':
        await help_cmd(update, context)
    else:
        # Auto detect input
        if re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{1,4}$', text.upper()):
            context.args = [text]
            await vehicle_cmd(update, context)
        elif re.match(r'^\d{10,12}$', text):
            context.args = [text]
            await phone_cmd(update, context)
        elif re.match(r'^\d{1,3}(\.\d{1,3}){3}$', text):
            context.args = [text]
            await ip_cmd(update, context)
        elif re.match(r'^\d{6}$', text):
            context.args = [text]
            await bin_cmd(update, context)
        else:
            await update.message.reply_text("Use menu buttons or /help")

# ===================== MAIN =====================
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("vehicle", vehicle_cmd))
    app.add_handler(CommandHandler("phone", phone_cmd))
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("bin", bin_cmd))
    app.add_handler(CommandHandler("password", password_cmd))
    app.add_handler(CommandHandler("encrypt", encrypt_cmd))
    app.add_handler(CommandHandler("decrypt", decrypt_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot Started...")
    app.run_polling()

if __name__ == '__main__':
    main()
