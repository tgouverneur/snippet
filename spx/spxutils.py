import string
import secrets

def randString(size=32, chars=string.ascii_letters + string.digits):
    """Return a cryptographically secure random string."""
    return ''.join(secrets.choice(chars) for _ in range(size))
