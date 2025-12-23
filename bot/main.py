"""
Telegram Bot for Analytics Mini App
This bot sends alerts and provides access to the Mini App
"""

import os
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
MINI_APP_URL = os.getenv('MINI_APP_URL', 'http://localhost:5173')

# Chat IDs for alerts (replace with your chat IDs)
ALERT_CHAT_IDS = [727013047, 718885452, 6775209607, 1139941966, 332270956]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message with Mini App button when the command /start is issued."""
    keyboard = [[
        InlineKeyboardButton(
            "📊 Відкрити Аналітику",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '👋 Вітаю в системі аналітики!\n\n'
        'Натисніть кнопку нижче щоб відкрити панель аналітики:\n\n'
        '📊 Інтерактивні дашборди\n'
        '🎯 Аналітика по лідам\n'
        '💰 Звіти по продажам\n'
        '⚠️ Система алертів',
        reply_markup=reply_markup
    )


async def send_daily_alerts():
    """Send daily alerts to all chat IDs"""
    try:
        # Get alerts from API
        response = requests.get(f'{API_BASE_URL}/api/alerts/', timeout=30)

        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])

            if alerts:
                # Format alert message
                message = "⚠️ <b>Щоденні алерти</b>\n\n"

                for alert in alerts:
                    severity_emoji = {
                        'critical': '🔴',
                        'warning': '🟡',
                        'info': '🔵'
                    }.get(alert['severity'], 'ℹ️')

                    message += f"{severity_emoji} <b>{alert['title']}</b>\n"
                    message += f"{alert['description']}\n\n"

                # Send to all chat IDs
                for chat_id in ALERT_CHAT_IDS:
                    # Add Mini App button
                    keyboard = [[
                        InlineKeyboardButton(
                            "📊 Відкрити Аналітику",
                            web_app=WebAppInfo(url=MINI_APP_URL)
                        )
                    ]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    # Send message (you'll need to pass bot instance here)
                    # await bot.send_message(
                    #     chat_id=chat_id,
                    #     text=message,
                    #     parse_mode='HTML',
                    #     reply_markup=reply_markup
                    # )
                    pass

    except Exception as e:
        print(f"[Alert Error] {str(e)}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "📊 <b>Команди бота:</b>\n\n"
        "/start - Відкрити панель аналітики\n"
        "/help - Показати цю допомогу\n\n"
        "<b>Функціонал:</b>\n"
        "• Інтерактивні дашборди\n"
        "• Drill-down аналітика\n"
        "• Система алертів\n"
        "• Звіти по періодам\n"
    )

    await update.message.reply_text(help_text, parse_mode='HTML')


def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
