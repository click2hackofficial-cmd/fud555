import subprocess
from config import APKSIGNER_PATH, ZIPALIGN_PATH, KEYSTORE_PATH, KEYSTORE_PASS

def sign_apk(unsigned_apk: str, output_apk: str):
    aligned = unsigned_apk.replace(".apk", "_aligned.apk")

    subprocess.run([
        ZIPALIGN_PATH, "-v", "-p", "4",
        unsigned_apk, aligned
    ], check=True, capture_output=True)

    subprocess.run([
        APKSIGNER_PATH, "sign",
        "--ks", KEYSTORE_PATH,
        "--ks-pass", f"pass:{KEYSTORE_PASS}",
        "--out", output_apk,
        aligned
    ], check=True, capture_output=True)