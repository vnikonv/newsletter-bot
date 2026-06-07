import os
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from modules.bot.handlers import register_handlers


def _load_env():
    # prefer project config .env but fall back to system env
    cfg = Path(__file__).resolve().parent / "modules" / "config" / ".env"
    if cfg.exists():
        load_dotenv(dotenv_path=cfg)


def main():
    _load_env()

    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN environment variable is required to run the bot")

    app = ApplicationBuilder().token(token).build()

    register_handlers(app)

    print("Starting bot. Press Ctrl-C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
