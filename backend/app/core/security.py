import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import settings


class TokenError(ValueError):
    pass


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    n, r, p, length = 2**14, 8, 1, 64
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=length)
    return "$".join(
        [
            "scrypt",
            str(n),
            str(r),
            str(p),
            _b64url_encode(salt),
            _b64url_encode(digest),
        ]
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        expected_bytes = _b64url_decode(expected)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_b64url_decode(salt),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected_bytes),
        )
        return hmac.compare_digest(actual, expected_bytes)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    now = int(time.time())
    lifetime = (expires_minutes or settings.access_token_minutes) * 60
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + lifetime,
        "iss": "storeflow",
    }
    signing_input = f"{_b64url_encode(json.dumps(header, separators=(',', ':')).encode())}.{_b64url_encode(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = hmac.new(settings.auth_secret_key.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        signing_input = f"{encoded_header}.{encoded_payload}"
        expected = hmac.new(settings.auth_secret_key.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
        actual = _b64url_decode(encoded_signature)
        if not hmac.compare_digest(expected, actual):
            raise TokenError("Invalid token signature")
        header = json.loads(_b64url_decode(encoded_header))
        payload = json.loads(_b64url_decode(encoded_payload))
        if header.get("alg") != "HS256" or payload.get("iss") != "storeflow":
            raise TokenError("Invalid token metadata")
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise TokenError("Token expired")
        if not payload.get("sub"):
            raise TokenError("Token subject missing")
        return payload
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        if isinstance(exc, TokenError):
            raise
        raise TokenError("Invalid token") from exc
