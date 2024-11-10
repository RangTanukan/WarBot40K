import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from scraper import get_wiki_summary_and_link  # Ensure that the scraper function name is correct

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not TELEGRAM_API_TOKEN:
    logger.error("TELEGRAM_API_TOKEN not defined. Make sure the .env file contains this variable.")
    raise ValueError("TELEGRAM_API_TOKEN is not defined.")

# Function to handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    logger.info(f"Received message: {question}")

    logger.info(f"Searching for an answer to the question: {question}. Starting scraping...")
    summary, link = get_wiki_summary_and_link(question)  # Modified to call the correct function

    if summary:
        response = f"{summary}\n\nYou can read more here: {link}"
    else:
        response = "I couldn't find information on this topic."

    await update.message.reply_text(response)


# Handling the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /start command")
    await update.message.reply_text('Hello! Ask me anything about Warhammer 40K.')


# Handling unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received unknown command")
    await update.message.reply_text("Sorry, I do not recognize this command.")


def main():
    # Create the Telegram application
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    if not TELEGRAM_API_TOKEN:
        logger.error("Bot token not available.")
        return

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Unknown command handlers
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
