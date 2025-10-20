import os
import re
import tempfile
import shutil
import time
import fcntl
from stat import S_IMODE

# Reference:
# https://chatgpt.com/share/68f5acb9-9b8c-8005-8608-3819b359044b

AUTHORIZED_KEYS_PATH = "./.ssh/authorized_keys"
COMMAND_TEMPLATE = (
    'command="/config/bin/command_router.sh --profile default --key-id {email}",'
    'no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding {key}'
)

KEY_PATTERN = re.compile(
    r'^(ssh-(rsa|dss)|ssh-ed25519|ecdsa-sha2-nistp(256|384|521))\s+[A-Za-z0-9+/=]+(?:\s+.+)?$'
)


def validate_key_format(key: str) -> bool:
    return bool(KEY_PATTERN.match(key.strip()))


def make_entry(email: str, key: str) -> str:
    safe_email = email.replace('"', '\\"')
    return COMMAND_TEMPLATE.format(email=safe_email, key=key.strip())


def backup_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(path), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"authorized_keys.bak.{ts}")
    shutil.copy2(path, backup_path)
    return backup_path


def add_authorized_key(email: str, key: str) -> dict:
    if not validate_key_format(key):
        return {"error": "Invalid SSH public key format"}

    entry = make_entry(email, key)
    pubkey = key.split()[-1]

    path = AUTHORIZED_KEYS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dirdata = os.path.abspath(AUTHORIZED_KEYS_PATH)

    backup_path = backup_file(path)
    existing = ""

    # Leer con bloqueo
    if os.path.exists(path):
        with open(path, "r+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            existing = fh.read()
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    lines = existing.splitlines()
    normalized_existing = set(line.strip() for line in lines if line.strip())
    existing_pubkeys = {line.strip().split()[-1] for line in normalized_existing if line.strip()}

    if pubkey in existing_pubkeys:
        return {"status": "duplicate", "message": "Key already exists"}

    normalized_existing.add(entry.strip())
    final_content = "\n".join(normalized_existing) + "\n"

    # Escritura atómica
    dirn = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=".authkeys_tmp_", dir=dirn)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(final_content)
        f.flush()
        os.fsync(f.fileno())

    if os.path.exists(path):
        st = os.stat(path)
        os.chmod(tmp, S_IMODE(st.st_mode))
        shutil.chown(tmp, user=st.st_uid, group=st.st_gid)
    else:
        os.chmod(tmp, 0o600)
    os.replace(tmp, path)

    return {
        "status": "added",
        "backup": backup_path,
        "entry": entry,
    }
