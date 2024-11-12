import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from scraper import get_wiki_summary_and_link  # Ensure the scraper function is correct
from datetime import datetime, timedelta

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not TELEGRAM_API_TOKEN:
    logger.error("TELEGRAM_API_TOKEN not defined. Make sure the .env file contains this variable.")
    raise ValueError("TELEGRAM_API_TOKEN is not defined.")

# State for tracking active sessions
active_sessions = {}
INACTIVITY_TIMEOUT = 300  # 5 minutes timeout for inactivity


# Function to handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text.strip().lower()

    # Check if the user is active in a session
    if user_id in active_sessions and active_sessions[user_id]["active"]:
        # Check for inactivity timeout
        if datetime.now() - active_sessions[user_id]["last_interaction"] > timedelta(seconds=INACTIVITY_TIMEOUT):
            # Inactivity timeout, deactivate the session
            logger.info(f"User {user_id} inactive for too long. Deactivating session.")
            active_sessions[user_id]["active"] = False
            await update.message.reply_text("Session expired due to inactivity. Type /start to begin again.")
            return

        if message_text in ['yes', 'no']:
            # Handle "Yes" or "No" responses
            await handle_continue_or_end(update, context, message_text)
        else:
            # Handle regular queries
            logger.info(f"Searching for an answer to the question: {message_text}. Starting scraping...")
            summary, link = get_wiki_summary_and_link(message_text)  # Fetch data using scraper

            if summary:
                response = f"{summary}\n\nYou can read more here: {link}"
            else:
                response = "I couldn't find information on this topic."

            # Update last interaction time
            active_sessions[user_id]["last_interaction"] = datetime.now()

            # Ask if the user wants to search again (no buttons, just text)
            await update.message.reply_text(response + "\n\nWould you like to look for something else? (Yes/No)")

    else:
        await update.message.reply_text("Please type /start to begin a new session.")


# Handling the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"Received /start command from {user_id}")

    # Start a new session for the user
    active_sessions[user_id] = {
        "active": True,
        "last_interaction": datetime.now()
    }

    await update.message.reply_text('Hello! Ask me anything about Warhammer 40K. Type your query directly.')


# Handling user responses for continuing the search or not
async def handle_continue_or_end(update: Update, context: ContextTypes.DEFAULT_TYPE, user_response: str):
    user_id = update.message.from_user.id

    if user_id in active_sessions and active_sessions[user_id]["active"]:
        # Update last interaction time
        active_sessions[user_id]["last_interaction"] = datetime.now()

        if user_response == "yes":
            await update.message.reply_text('Great! Ask me your next query.')
        elif user_response == "no":
            # End the session for the user
            active_sessions[user_id]["active"] = False
            await update.message.reply_text("Thank you for using the bot! To start again, type /start.")
        else:
            await update.message.reply_text("Please reply with 'Yes' or 'No'.")
    else:
        await update.message.reply_text("Session has ended or expired. Type /start to begin again.")


# Handle Telegram rate limiting (Flood control)
async def handle_flood_control_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error):
    if isinstance(error, telegram.error.RetryAfter):
        retry_after = error.retry_after
        await asyncio.sleep(retry_after)
        await update.message.reply_text("Sorry, I was rate-limited. Please try again shortly.")
    else:
        raise error


def main():
    # Create the Telegram application
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    if not TELEGRAM_API_TOKEN:
        logger.error("Bot token not available.")
        return

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # Message handlers for querying information
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Message handlers for 'Yes' or 'No' responses (for continuing or ending)
    application.add_handler(MessageHandler(filters.TEXT, handle_continue_or_end))

    # Error handling for rate-limiting (flood control)
    application.add_error_handler(handle_flood_control_error)

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
