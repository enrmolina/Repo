import os

import httpx
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN", "")
    secret = os.getenv("TELEGRAM_SECRET", "")
    public_url = os.getenv("PUBLIC_URL", "").rstrip("/")
    if not token or not secret or not public_url:
        raise SystemExit("Faltan TELEGRAM_TOKEN, TELEGRAM_SECRET o PUBLIC_URL en .env")

    response = httpx.post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        json={"url": f"{public_url}/telegram", "secret_token": secret},
        timeout=20.0,
    )
    print(response.text)
    response.raise_for_status()


if __name__ == "__main__":
    main()
