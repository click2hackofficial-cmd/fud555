import os
import re
import random
import string

def rand_name(length=12):
    return ''.join(random.choices(string.ascii_letters, k=length))

def mutate_smali(decompiled_dir: str):
    smali_dir = os.path.join(decompiled_dir, "smali")
    rename_map = {}

    for root, _, files in os.walk(smali_dir):
        for fname in files:
            if not fname.endswith(".smali"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Rename private methods
            for match in re.finditer(r'\.method private (\w+)\(', content):
                orig = match.group(1)
                if orig not in rename_map and orig not in ("init", "clinit"):
                    rename_map[orig] = rand_name()

            for orig, new in rename_map.items():
                content = content.replace(orig, new)

            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)