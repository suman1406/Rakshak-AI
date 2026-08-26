import hashlib
import hmac

def hash_secret(value: str, salt: str = "rakshak") -> str:
    return hashlib.pbkdf2_hmac("sha256", value.encode(), salt.encode(), 120_000).hex()

def verify_secret(value: str, expected: str, salt: str = "rakshak") -> bool:
    return hmac.compare_digest(hash_secret(value, salt), expected)

