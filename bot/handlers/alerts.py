"""
Alert handlers for sending notifications to Telegram
"""

import requests
from typing import List
from telegram import Bot


class AlertHandler:
    """Handler for sending alerts via Telegram"""

    def __init__(self, bot_token: str, api_base_url: str):
        self.bot = Bot(token=bot_token)
        self.api_base_url = api_base_url

    async def fetch_alerts(self) -> List[dict]:
        """Fetch current alerts from API"""
        try:
            response = requests.get(
                f'{self.api_base_url}/api/alerts/',
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('alerts', [])

            return []

        except Exception as e:
            print(f"[Alert Fetch Error] {str(e)}")
            return []

    def format_alert_message(self, alerts: List[dict]) -> str:
        """Format alerts into Telegram message"""
        if not alerts:
            return None

        message = "⚠️ <b>Щоденні алерти</b>\n\n"

        for alert in alerts:
            severity_emoji = {
                'critical': '🔴',
                'warning': '🟡',
                'info': '🔵'
            }.get(alert['severity'], 'ℹ️')

            message += f"{severity_emoji} <b>{alert['title']}</b>\n"
            message += f"{alert['description']}\n"

            if alert.get('manager_name'):
                message += f"👤 {alert['manager_name']}\n"

            message += "\n"

        return message

    async def send_alerts(self, chat_ids: List[int], mini_app_url: str):
        """Send alerts to specified chat IDs"""
        alerts = await self.fetch_alerts()

        if not alerts:
            print("[Alerts] No alerts to send")
            return

        message = self.format_alert_message(alerts)

        if not message:
            return

        # Send to each chat
        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                print(f"[Alerts] Sent to chat {chat_id}")

            except Exception as e:
                print(f"[Alert Send Error] Chat {chat_id}: {str(e)}")
