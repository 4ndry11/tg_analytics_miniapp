"""
Notification handlers for sending daily/weekly reports
"""

import requests
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


class NotificationHandler:
    """Handler for sending reports via Telegram"""

    def __init__(self, bot_token: str, api_base_url: str, mini_app_url: str):
        self.bot = Bot(token=bot_token)
        self.api_base_url = api_base_url
        self.mini_app_url = mini_app_url

    async def send_daily_report(self, chat_ids: list, date: str = None):
        """Send daily report to chat IDs"""
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        try:
            # Fetch report from API
            response = requests.get(
                f'{self.api_base_url}/api/reports/daily?date={date}',
                timeout=30
            )

            if response.status_code != 200:
                print(f"[Report Error] Status: {response.status_code}")
                return

            report = response.json()

            # Format message
            message = self.format_daily_report(report)

            # Add button
            keyboard = [[
                InlineKeyboardButton(
                    "📊 Детальна аналітика",
                    web_app=WebAppInfo(url=self.mini_app_url)
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send to all chats
            for chat_id in chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                    print(f"[Report] Sent daily report to {chat_id}")

                except Exception as e:
                    print(f"[Report Send Error] Chat {chat_id}: {str(e)}")

        except Exception as e:
            print(f"[Daily Report Error] {str(e)}")

    def format_daily_report(self, report: dict) -> str:
        """Format daily report into Telegram message"""
        leads_metrics = report.get('leads', {}).get('metrics', {})
        sales_data = report.get('sales', {})
        finmap_data = report.get('finmap', {})

        message = f"☀️ <b>Звіт за {report.get('date')}</b>\n\n"

        # Leads section
        message += f"🎯 <b>Ліди:</b> {leads_metrics.get('total_leads', 0)}\n"
        message += f"📈 <b>Продажі:</b> {leads_metrics.get('total_deals', 0)}\n"

        total_leads = leads_metrics.get('total_leads', 0)
        total_deals = leads_metrics.get('total_deals', 0)
        cr = (total_deals / total_leads * 100) if total_leads > 0 else 0

        message += f"💹 <b>CR%:</b> {cr:.2f}%\n\n"

        # Sales section
        message += f"💰 <b>Продажі на суму:</b> {sales_data.get('total_amount', 0):,.0f} грн\n"
        message += f"📄 <b>Контрактів:</b> {sales_data.get('total_contracts', 0)}\n\n"

        # Finmap
        if finmap_data and finmap_data.get('total', 0) > 0:
            message += f"💵 <b>Finmap надходження:</b> {finmap_data['total']:,.2f} грн\n"
            message += f"(Операцій: {finmap_data.get('count', 0)})\n\n"

        # Department reaction time
        if leads_metrics.get('department_median'):
            message += f"⏱ <b>Час реакції відділу:</b> {leads_metrics['department_median']}\n"

        return message
