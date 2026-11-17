import os

import httpx
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN", "")
    if not token:
        raise SystemExit("Falta TELEGRAM_TOKEN en .env")

    response = httpx.get(
        f"https://api.telegram.org/bot{token}/getWebhookInfo",
        timeout=20.0,
    )
    print(response.text)
    response.raise_for_status()


if __name__ == "__main__":
    main()
