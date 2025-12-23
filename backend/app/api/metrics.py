from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
from ..core.config import settings
from ..services.leads_service import LeadsService
from ..services.sales_service import SalesService
from ..services.alerts_service import AlertsService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

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


@router.get("/leads")
async def get_leads_metrics(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    manager_id: Optional[str] = Query(None, description="Filter by manager ID")
):
    """Get leads metrics with drill-down capability"""
    try:
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        leads_df = leads_service.get_leads_data(date, date)
        users_df = leads_service.get_users()
        statuses_df = leads_service.get_statuses()

        if leads_df.empty:
            return {
                'total_leads': 0,
                'by_source': {},
                'by_manager': {},
                'by_status': {},
                'details': []
            }

        # Filter by manager if specified
        if manager_id:
            leads_df = leads_df[leads_df['ASSIGNED_BY_ID'] == manager_id]

        # Merge with users and statuses
        leads_with_users = leads_df.merge(users_df, left_on='ASSIGNED_BY_ID', right_on='ID', how='inner')
        full_data = leads_with_users.merge(statuses_df, on='STATUS_ID', how='inner')

        # Aggregations
        by_source = full_data['UTM_SOURCE'].value_counts().to_dict()
        by_manager = full_data['FULL_NAME'].value_counts().to_dict()
        by_status = full_data['NAME'].value_counts().to_dict()

        # Details for drill-down
        details = full_data[['ID_x', 'DATE_CREATE', 'UTM_SOURCE', 'FULL_NAME', 'NAME', 'taken_in_work', 'time_taken_in_work']].to_dict('records')

        return {
            'date': date,
            'total_leads': len(leads_df),
            'by_source': by_source,
            'by_manager': by_manager,
            'by_status': by_status,
            'details': details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/sales")
async def get_sales_metrics(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    manager_id: Optional[str] = Query(None, description="Filter by manager ID")
):
    """Get sales metrics with drill-down capability"""
    try:
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        deals_df = sales_service.get_deals_data(date, date)
        users_df = sales_service.get_users()

        if deals_df.empty:
            return {
                'total_amount': 0,
                'total_contracts': 0,
                'by_source': {},
                'by_manager': {},
                'details': []
            }

        # Filter by manager if specified
        if manager_id:
            deals_df = deals_df[deals_df['ASSIGNED_BY_ID'] == manager_id]

        # Merge with users
        full_data = deals_df.merge(users_df, how='inner', left_on='ASSIGNED_BY_ID', right_on='ID')
        full_data["OPPORTUNITY"] = full_data["OPPORTUNITY"].astype(float)

        # Aggregations
        by_source = full_data.groupby('UTM_SOURCE')['OPPORTUNITY'].sum().to_dict()
        by_manager = full_data.groupby('FULL_NAME')['OPPORTUNITY'].sum().to_dict()

        return {
            'date': date,
            'total_amount': float(full_data['OPPORTUNITY'].sum()),
            'total_contracts': len(full_data),
            'by_source': by_source,
            'by_manager': by_manager,
            'details': full_data[['ID_x', 'OPPORTUNITY', 'FULL_NAME', 'UTM_SOURCE', 'CLOSEDATE']].to_dict('records')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/conversion")
async def get_conversion_metrics(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Get conversion metrics for period"""
    try:
        leads_df = leads_service.get_leads_data(start_date, end_date)
        deals_df = leads_service.get_deals_data(start_date, end_date)
        users_df = leads_service.get_users()

        if leads_df.empty:
            return {
                'total_cr': 0,
                'by_manager': []
            }

        metrics = leads_service.calculate_metrics(leads_df, deals_df, users_df)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_leads': metrics['total_leads'],
            'total_deals': metrics['total_deals'],
            'total_cr': round((metrics['total_deals'] / metrics['total_leads'] * 100) if metrics['total_leads'] > 0 else 0, 2),
            'by_manager': metrics['by_manager']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversion metrics: {str(e)}")


@router.get("/manager/{manager_id}")
async def get_manager_detail(
    manager_id: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Get detailed metrics for specific manager"""
    try:
        # Get leads for this manager
        leads_df = leads_service.get_leads_data(start_date, end_date)
        deals_df = leads_service.get_deals_data(start_date, end_date)
        users_df = leads_service.get_users()
        statuses_df = leads_service.get_statuses()

        # Filter by manager
        manager_leads = leads_df[leads_df['ASSIGNED_BY_ID'] == manager_id]
        manager_deals = deals_df[deals_df['ASSIGNED_BY_ID'] == manager_id] if not deals_df.empty else pd.DataFrame()

        # Get manager name
        manager_info = users_df[users_df['ID'] == manager_id]
        manager_name = manager_info.iloc[0]['FULL_NAME'] if not manager_info.empty else 'Unknown'

        # Calculate metrics
        total_leads = len(manager_leads)
        total_deals = len(manager_deals) if not manager_deals.empty else 0
        cr = round((total_deals / total_leads * 100) if total_leads > 0 else 0, 2)

        # Reaction time
        leads_with_time = manager_leads[manager_leads['time_taken_in_work'].notna()]
        avg_reaction_time = leads_with_time['time_taken_in_work'].mean() if not leads_with_time.empty else None

        # By status
        manager_leads_full = manager_leads.merge(statuses_df, on='STATUS_ID', how='inner')
        by_status = manager_leads_full['NAME'].value_counts().to_dict()

        # By source
        by_source = manager_leads['UTM_SOURCE'].value_counts().to_dict()

        return {
            'manager_id': manager_id,
            'manager_name': manager_name,
            'start_date': start_date,
            'end_date': end_date,
            'total_leads': total_leads,
            'total_deals': total_deals,
            'cr_percent': cr,
            'avg_reaction_time': str(avg_reaction_time) if avg_reaction_time else None,
            'by_status': by_status,
            'by_source': by_source,
            'leads_list': manager_leads[['ID', 'DATE_CREATE', 'UTM_SOURCE', 'STATUS_ID', 'taken_in_work']].to_dict('records')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting manager details: {str(e)}")
