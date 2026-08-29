import os
import re
import base64

def xor_encrypt(s: str, key: int = 0x42) -> str:
    return base64.b64encode(bytes([ord(c) ^ key for c in s])).decode()

def decrypt_smali_stub(encrypted: str, key: int = 0x42) -> str:
    # Smali stub: injects a decrypt call inline
    return f'''
    const-string v0, "{encrypted}"
    const/16 v1, {key}
    invoke-static {{v0, v1}}, Lcom/util/StringDecryptor;->decrypt(Ljava/lang/String;I)Ljava/lang/String;
    move-result-object v0
'''

def encrypt_strings(decompiled_dir: str):
    smali_dir = os.path.join(decompiled_dir, "smali")
    pattern = re.compile(r'const-string (v\d+|p\d+), "(.+?)"')

    for root, _, files in os.walk(smali_dir):
        for fname in files:
            if not fname.endswith(".smali"):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            def replacer(m):
                reg = m.group(1)
                val = m.group(2)
                if len(val) < 4:
                    return m.group(0)
                enc = xor_encrypt(val)
                return decrypt_smali_stub(enc).replace("v0", reg)

            new_content = pattern.sub(replacer, content)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)