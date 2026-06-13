from flask import request, jsonify, current_app
from functools import wraps
from jose.exceptions import JWTError, ExpiredSignatureError
from jose import jwt
import time


def encode_token(customer_id):
    """Create a signed JWT token for a customer. Expires in 1 hour."""
    payload = {
        "sub": str(customer_id),   # JWT spec requires sub to be a string
        "iat": int(time.time()),   # issued at (Unix timestamp)
        "exp": int(time.time()) + 3600,  # expires in 1 hour
    }

    secret = current_app.config["SECRET_KEY"]
    token = jwt.encode(payload, secret, algorithm="HS256")

    print(f"[DEBUG] encode_token: customer_id={customer_id}")
    print(f"[DEBUG] encode_token: payload={payload}")
    print(f"[DEBUG] encode_token: token={token}")

    return token


def token_required(f):
    """Decorator that reads Bearer token from Authorization header and injects customer_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        print(f"[DEBUG] token_required: Authorization header={auth_header!r}")

        # Check header format
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header. Use: Bearer <token>"}), 401

        # Extract the raw token (split on first space only, strip any whitespace)
        token = auth_header.split(" ", 1)[1].strip()
        print(f"[DEBUG] token_required: extracted token={token!r}")

        secret = current_app.config["SECRET_KEY"]
        print(f"[DEBUG] token_required: using SECRET_KEY={secret!r}")

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            print(f"[DEBUG] token_required: decoded payload={payload}")

            customer_id = int(payload.get("sub"))  # convert back to int
            print(f"[DEBUG] token_required: customer_id={customer_id}")

        except ExpiredSignatureError:
            print("[DEBUG] token_required: token is EXPIRED")
            return jsonify({"error": "Token has expired. Please log in again."}), 401

        except JWTError as e:
            print(f"[DEBUG] token_required: JWTError -> {e}")
            return jsonify({"error": "Invalid token"}), 401

        # Pass customer_id as the first argument into the protected route
        return f(customer_id, *args, **kwargs)

    return decorated
