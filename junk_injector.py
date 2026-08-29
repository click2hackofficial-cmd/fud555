import os
import random
import string

def rand_name(k=10):
    return ''.join(random.choices(string.ascii_lowercase, k=k))

JUNK_TEMPLATE = """
.class public L{pkg}/{cls};
.super Ljava/lang/Object;

.method public constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static {m1}()Ljava/lang/String;
    .registers 1
    const-string v0, "{val1}"
    return-object v0
.end method

.method public static {m2}()I
    .registers 1
    const/16 v0, {val2}
    return v0
.end method
"""

def inject_junk(decompiled_dir: str, count: int = 20):
    smali_dir = os.path.join(decompiled_dir, "smali")
    junk_pkg = rand_name(6)
    junk_dir = os.path.join(smali_dir, junk_pkg)
    os.makedirs(junk_dir, exist_ok=True)

    for _ in range(count):
        cls_name = rand_name(8).capitalize()
        smali_content = JUNK_TEMPLATE.format(
            pkg=junk_pkg,
            cls=cls_name,
            m1=rand_name(7),
            m2=rand_name(7),
            val1=''.join(random.choices(string.printable[:62], k=12)),
            val2=random.randint(1, 9999)
        )
        fpath = os.path.join(junk_dir, f"{cls_name}.smali")
        with open(fpath, "w") as f:
            f.write(smali_content)