import os
import re
import random
import string

def random_package_name():
    parts = []
    for _ in range(3):
        parts.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 8))))
    return '.'.join(parts)

def randomize_manifest(decompiled_dir: str):
    manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Randomize package name
    new_pkg = random_package_name()
    content = re.sub(r'package="[^"]+"', f'package="{new_pkg}"', content)

    # Add fake permissions to bury real ones
    fake_perms = [
        '<uses-permission android:name="android.permission.FLASHLIGHT"/>',
        '<uses-permission android:name="android.permission.SET_WALLPAPER"/>',
        '<uses-permission android:name="android.permission.VIBRATE"/>',
    ]
    random.shuffle(fake_perms)
    injection_point = content.find('<application')
    for perm in fake_perms:
        content = content[:injection_point] + perm + '\n' + content[injection_point:]

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)