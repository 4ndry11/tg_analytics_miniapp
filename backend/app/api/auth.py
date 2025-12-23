from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import hmac
import hashlib
import json
from urllib.parse import parse_qs

router = APIRouter(prefix="/api/auth", tags=["auth"])


def validate_telegram_web_app_data(init_data: str, bot_token: str) -> bool:
    """
    Validate Telegram Mini App init data
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        parsed_data = parse_qs(init_data)
        hash_value = parsed_data.get('hash', [''])[0]

        if not hash_value:
            return False

        # Remove hash from data
        data_check_string = '\n'.join(
            [f"{k}={v[0]}" for k, v in sorted(parsed_data.items()) if k != 'hash']
        )

        # Create secret key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return calculated_hash == hash_value

    except Exception as e:
        print(f"[Auth Error] {str(e)}")
        return False


@router.post("/telegram")
async def validate_telegram_init_data(
    x_telegram_init_data: Optional[str] = Header(None)
):
    """Validate Telegram Mini App authentication"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram init data")

    # For development, you can skip validation
    # In production, uncomment this:
    # from ..core.config import settings
    # if not validate_telegram_web_app_data(x_telegram_init_data, settings.TELEGRAM_BOT_TOKEN):
    #     raise HTTPException(status_code=401, detail="Invalid Telegram init data")

    return {"status": "authenticated"}
