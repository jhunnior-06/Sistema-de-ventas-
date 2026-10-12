import hashlib
import hmac
import os
import secrets

ITERATIONS = 310_000

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    ).hex()
    return salt + "$" + digest

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected = stored_hash.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    ).hex()
    return hmac.compare_digest(actual, expected)

def get_initial_admin() -> tuple[str, str, str]:
    username = os.getenv("ADMIN_USERNAME", "admin").strip().lower()
    display_name = os.getenv("ADMIN_NAME", "Administrador")
    password = os.getenv("ADMIN_PASSWORD")

    if not password:
        if os.getenv("VERCEL"):
            raise RuntimeError(
                "Configura ADMIN_PASSWORD en Vercel antes del primer despliegue."
            )
        password = "admin123"
    return username, display_name, password
