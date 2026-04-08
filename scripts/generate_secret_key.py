"""Print a URL-safe secret suitable for SECRET_KEY. Usage: python scripts/generate_secret_key.py"""
import secrets

if __name__ == "__main__":
    print(secrets.token_urlsafe(48))
