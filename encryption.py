from cryptography.fernet import Fernet
import config

def get_fernet():
    key = config.ENCRYPTION_KEY
    if not key:
        # Generate a temporary key if none set (for testing only)
        key = Fernet.generate_key().decode()
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt(text: str) -> str:
    if not text:
        return ""
    try:
        return get_fernet().encrypt(text.encode("utf-8")).decode("utf-8")
    except Exception:
        return text

def decrypt(token: str) -> str:
    if not token:
        return ""
    try:
        return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return token

def generate_new_key() -> str:
    """Run this once to get your encryption key — paste it into Streamlit secrets"""
    key = Fernet.generate_key().decode()
    print(f"\nYour ENCRYPTION_KEY (copy this into Streamlit secrets):\n{key}\n")
    return key

if __name__ == "__main__":
    generate_new_key()
