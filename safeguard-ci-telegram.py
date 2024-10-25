import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")

async def start(update, context):
    # Check if the command is /migrate
    if update.message.text == '/migrate safeguard app':  
        keyboard = [
            [InlineKeyboardButton("Migrate Dev DB", callback_data='migrate_dev')],
            [InlineKeyboardButton("Migrate Stag DB", callback_data='migrate_stag')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Choose an environment to migrate:', reply_markup=reply_markup)
    else:
        await update.message.reply_text("Invalid command. Are you supposed to be interacting with me?")

async def button(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'migrate_dev':
        environment = 'dev'
    elif query.data == 'migrate_stag':
        environment = 'uat'
    else:
        await query.edit_message_text(text="Invalid input")
        return

    try:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/dispatches"  
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {  
            "event_type": "telegram_dispatch",
            "client_payload": {
                "environment": environment
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        await query.edit_message_text(text=f"Workflow dispatched for {environment} environment!")
    except requests.exceptions.RequestException as e:
        await query.edit_message_text(text=f"Error dispatching workflow: {e}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add the command handler for /migrate
    application.add_handler(CommandHandler("migrate", start))  
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()