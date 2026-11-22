import hashlib
import hmac
import secrets
import threading
import json

users = {}
users_lock = threading.Lock()

SCRYPT_N = 2**14
SCRYPT_R = 8 
SCRYPT_P = 1
SCRYPT_DKLEN = 32 
SALT_SIZE = 16

def hash_password(password: str) -> str:
    """
    Hash a password scrypt with a randomly generated salt.

    Stored format:
        scrypt$N$r$p$salt$derived_hash
    """

    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    
    salt = secrets.token_bytes(SALT_SIZE)

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN
    )

    return (
        f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}$"
        f"{salt.hex()}${derived_key.hex()}"
    )

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored scrypt hash.

    Returns False if the password or stored hash is invalid.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False
    
    try:
        algorithm, n, r, p, salt_hex, digest_hex = stored_hash.split("$")

        if algorithm != "scrypt":
            return False

        n = int(n)
        r = int(r)
        p = int(p)

        if (n, r, p) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False
        
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)

        if len(salt) != SALT_SIZE:
            return False
        
        if len(expected_digest) != SCRYPT_DKLEN:
            return False

        actual_digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=SCRYPT_DKLEN
        )

        return hmac.compare_digest(
            actual_digest,
            expected_digest
        )
    except (ValueError, TypeError, UnicodeDecodeError):
        return False

def json_response(status_code, message):
    """Create a consistent JSON response."""

    return (
        status_code,
        "application/json",
        json.dumps({"message": message})
    )

def parse_user_data(body):
    """
    Parse and validate the request body.

    Raises:
        ValueError: If JSON is invalid or not a JSON object.
    """

    try:
        data = json.loads(body)

    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid JSON") from exc 
    
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        raise ValueError("Missing or invalid username")

    if not isinstance(password, str) or not password:
        raise ValueError("Missing or invalid password")
    
    return {
        "username": username.strip(),
        "password": password
    }

def home():
    return 200, "text/plain", "Hello, Welcome to the http-server home page"

def about():
    return 200, "text/plain", "This is the about page"

def api():
    data = {
        "name" : "Vanika",
        "role" : "Creator"
    }

    return 200, "application/json", json.dumps(data)

def login(body):
    try:
        data = parse_user_data(body)

    except ValueError as exc:
        return json_response(400, str(exc))

    username = data["username"]
    password = data["password"]

    with users_lock:
        stored_hash = users.get(username)
    
    if stored_hash is not None and verify_password(
        password,
        stored_hash
    ):
        return json_response(200, "Login success")
    
    return json_response(401, "Invalid credentials")
    
def signup(body):

    try:
        data = parse_user_data(body)

    except ValueError as exc:
        return json_response(400, str(exc))

    username = data["username"]
    password = data["password"]

    password_hash = hash_password(password)

    with users_lock:
        if username in users:
            return json_response(409, "User already exists")

        users[username] = password_hash

    return json_response(201, "User created")

    
def not_found():
    return 404, "text/plain", "404 Not Found"