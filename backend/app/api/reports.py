from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
from ..core.config import settings
from ..services.leads_service import LeadsService
from ..services.sales_service import SalesService, FinmapService
from ..services.alerts_service import AlertsService

router = APIRouter(prefix="/api/reports", tags=["reports"])

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

finmap_service = FinmapService(
    api_key=settings.FINMAP_API_KEY,
    company_id=settings.FINMAP_COMPANY_ID
)

alerts_service = AlertsService()


@router.get("/daily")
async def get_daily_report(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """Get daily report for specific date"""
    try:
        if not date:
            # Default to yesterday
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Get leads report
        leads_report = leads_service.get_full_report(date, date)

        # Get sales report
        sales_report = sales_service.get_full_report(date, date)

        # Get Finmap data
        finmap_data = finmap_service.get_income_for_date(date)

        # Get alerts
        prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        prev_leads_report = leads_service.get_full_report(prev_date, prev_date)

        alerts = alerts_service.get_all_alerts(
            current_leads_metrics=leads_report,
            current_sales_metrics=sales_report,
            previous_leads_metrics=prev_leads_report
        )

        return {
            'date': date,
            'period': 'daily',
            'leads': leads_report,
            'sales': sales_report,
            'finmap': finmap_data,
            'alerts': alerts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/weekly")
async def get_weekly_report(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """Get weekly report for date range"""
    try:
        if not start_date or not end_date:
            # Default to last 7 days
            end = datetime.now() - timedelta(days=1)
            start = end - timedelta(days=6)
            start_date = start.strftime('%Y-%m-%d')
            end_date = end.strftime('%Y-%m-%d')

        # Get leads report
        leads_report = leads_service.get_full_report(start_date, end_date)

        # Get sales report
        sales_report = sales_service.get_full_report(start_date, end_date)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'period': 'weekly',
            'leads': leads_report,
            'sales': sales_report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/monthly")
async def get_monthly_report(
    year: Optional[int] = Query(None, description="Year"),
    month: Optional[int] = Query(None, description="Month (1-12)")
):
    """Get monthly report"""
    try:
        if not year or not month:
            # Default to last month
            today = datetime.now()
            if today.month == 1:
                year = today.year - 1
                month = 12
            else:
                year = today.year
                month = today.month - 1

        # Calculate date range
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_year = year + 1
            end_month = 1
        else:
            end_year = year
            end_month = month + 1

        end_date_obj = datetime(end_year, end_month, 1) - timedelta(days=1)
        end_date = end_date_obj.strftime('%Y-%m-%d')

        # Get leads report
        leads_report = leads_service.get_full_report(start_date, end_date)

        # Get sales report
        sales_report = sales_service.get_full_report(start_date, end_date)

        return {
            'year': year,
            'month': month,
            'start_date': start_date,
            'end_date': end_date,
            'period': 'monthly',
            'leads': leads_report,
            'sales': sales_report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/custom")
async def get_custom_report(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Get custom period report"""
    try:
        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Get leads report
        leads_report = leads_service.get_full_report(start_date, end_date)

        # Get sales report
        sales_report = sales_service.get_full_report(start_date, end_date)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'period': 'custom',
            'leads': leads_report,
            'sales': sales_report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
