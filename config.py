import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
APKTOOL_PATH = "/usr/local/bin/apktool"
ZIPALIGN_PATH = "/usr/bin/zipalign"
APKSIGNER_PATH = "/usr/bin/apksigner"
KEYSTORE_PATH = "./keys/release.jks"
KEYSTORE_PASS = "yourpass"
WORK_DIR = "/tmp/fud_workspace"