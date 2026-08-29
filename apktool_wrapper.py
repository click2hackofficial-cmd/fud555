import subprocess
from config import APKTOOL_PATH

def decompile(apk_path: str, output_dir: str):
    subprocess.run([
        APKTOOL_PATH, "d", apk_path,
        "-o", output_dir,
        "--force",
        "--no-src"  # keep smali
    ], check=True, capture_output=True)

def recompile(decompiled_dir: str, output_apk: str):
    subprocess.run([
        APKTOOL_PATH, "b", decompiled_dir,
        "-o", output_apk
    ], check=True, capture_output=True)