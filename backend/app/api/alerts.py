from fastapi import APIRouter
from datetime import datetime, timedelta
from ..services.alerts_service import AlertsService
from ..services.leads_service import LeadsService
from ..services.sales_service import SalesService
from ..core.config import settings

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Initialize services
leads_service = LeadsService(
    domain=settings.BITRIX24_DOMAIN,
    user_id=settings.BITRIX24_USER_ID,
    leads_token=settings.BITRIX24_TOKEN_LEADS,
    users_token=settings.BITRIX24_TOKEN_USERS,
    status_token=settings.BITRIX24_TOKEN_STATUS
)

sales_service = SalesService(
    domain=settings.BITRIX24_DOMAIN,
    user_id=settings.BITRIX24_USER_ID,
    deals_token=settings.BITRIX24_TOKEN_DEALS,
    users_token=settings.BITRIX24_TOKEN_USERS
)

alerts_service = AlertsService()


@router.get("/")
async def get_current_alerts():
    """Get current alerts for yesterday"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    day_before = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

    # Get current metrics
    current_leads = leads_service.get_full_report(yesterday, yesterday)
    current_sales = sales_service.get_full_report(yesterday, yesterday)

    # Get previous day metrics for comparison
    previous_leads = leads_service.get_full_report(day_before, day_before)

    # Generate alerts
    alerts = alerts_service.get_all_alerts(
        current_leads_metrics=current_leads,
        current_sales_metrics=current_sales,
        previous_leads_metrics=previous_leads
    )

    return {"alerts": alerts}
