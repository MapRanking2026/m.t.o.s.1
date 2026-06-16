import base64
import json


def decode_jwt_payload_unverified(token: str) -> dict:
    parts = token.split(".")
    if len(parts) < 2:
        return {}

    payload_segment = parts[1]
    padding = "=" * (-len(payload_segment) % 4)
    decoded = base64.urlsafe_b64decode(payload_segment + padding)
    return json.loads(decoded.decode("utf-8"))

