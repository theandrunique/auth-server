from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from src.config import settings
from src.utils import UUIDEncoder
from src.well_known.config import public_key, public_key_pem


def create(
    payload: dict[str, Any],
) -> str:
    payload["iss"] = settings.DOMAIN_URL
    encoded = jwt.encode(
        payload=payload,
        key=settings.PRIVATE_KEY,
        algorithm=settings.ALGORITHM,
        json_encoder=UUIDEncoder,
        headers={
            "kid": public_key.key_id,
        },
    )
    return encoded


def decode(token: str, audience: str | None = None) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            jwt=token,
            key=public_key_pem,
            algorithms=[settings.ALGORITHM],
            issuer=settings.DOMAIN_URL,
            audience=settings.DOMAIN_URL,
        )
    except InvalidTokenError:
        return None
