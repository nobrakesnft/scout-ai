"""Run the Scout Bot."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.delivery.telegram_bot import TelegramBot

import structlog

# Simple logging setup
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(colors=True),
    ],
)

logger = structlog.get_logger(__name__)


def main():
    """Start the bot."""
    logger.info("Starting Scout Bot...")

    # Create and run bot (scheduler starts automatically)
    bot = TelegramBot()

    logger.info("Bot is running! Press Ctrl+C to stop.")

    try:
        bot.run_polling()
    except KeyboardInterrupt:
        logger.info("Stopped.")


if __name__ == "__main__":
    main()
