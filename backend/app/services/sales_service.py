from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
from .b24_service import B24Service
import requests


class SalesService:
    """Service for working with sales data"""

    def __init__(self, domain: str, user_id: int, deals_token: str, users_token: str):
        self.b24_deals = B24Service(domain, user_id, deals_token)
        self.b24_users = B24Service(domain, user_id, users_token)
        self.domain = domain

    def get_deals_data(self, start_date: str, end_date: str, category_id: int = 0) -> pd.DataFrame:
        """Get deals data for date range"""
        deal_filter = {
            "CATEGORY_ID": category_id,
            ">=CLOSEDATE": f'{start_date}T00:00:01',
            "<=CLOSEDATE": f'{end_date}T23:59:59',
            'STAGE_ID': 'WON'
        }

        select_fields = ["ID", "OPPORTUNITY", 'ASSIGNED_BY_ID', 'CLOSEDATE', 'UTM_SOURCE', 'UF_CRM_1695636781']
        deals = self.b24_deals.get_list("crm.deal.list", b24_filter=deal_filter, select=select_fields)

        if not deals:
            return pd.DataFrame()

        return pd.DataFrame(deals)

    def get_users(self) -> pd.DataFrame:
        """Get users data"""
        users = self.b24_users.get_list('user.get', select=['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME'])
        users_df = pd.DataFrame(users)[['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME']]
        users_df['FULL_NAME'] = users_df[['NAME', 'LAST_NAME', 'SECOND_NAME']].fillna('').agg(' '.join, axis=1).str.strip()
        return users_df[['ID', 'FULL_NAME']]

    def get_full_report(self, start_date: str, end_date: str) -> Dict:
        """Get full sales report with all analytics"""
        deals_df = self.get_deals_data(start_date, end_date)
        users_df = self.get_users()

        if deals_df.empty:
            return {
                'total_amount': 0,
                'total_contracts': 0,
                'by_manager': [],
                'by_source': [],
                'by_type': []
            }

        # Transform data
        full_data = deals_df.merge(users_df, how='inner', left_on='ASSIGNED_BY_ID', right_on='ID')
        full_data["OPPORTUNITY"] = full_data["OPPORTUNITY"].astype(float)
        full_data = full_data.rename(columns={
            'ID_x': 'deal_id',
            'OPPORTUNITY': 'contract_amount',
            'FULL_NAME': 'manager',
            'UF_CRM_1695636781': 'type_contract'
        })

        # Replace contract type codes
        full_data.type_contract = full_data.type_contract.replace({
            '1206': 'Банкрутство',
            '1207': 'Досудове'
        })

        # Analysis by contract type
        type_contracts_data = full_data.groupby('type_contract').agg({
            'contract_amount': 'sum',
            'deal_id': 'count'
        }).reset_index().rename(columns={'deal_id': 'number_of_contracts'})

        # Analysis by managers
        data_sales_by_managers = full_data.groupby('manager').aggregate({
            'contract_amount': 'sum',
            'CLOSEDATE': 'count'
        }).sort_values('contract_amount', ascending=False).reset_index()
        data_sales_by_managers = data_sales_by_managers.rename(columns={'CLOSEDATE': 'number_of_contracts'})

        # Analysis by sources
        data_sales_by_source = full_data.groupby('UTM_SOURCE').aggregate({
            'contract_amount': 'sum',
            'CLOSEDATE': 'count'
        }).sort_values('contract_amount', ascending=False).reset_index()
        data_sales_by_source = data_sales_by_source.rename(columns={'CLOSEDATE': 'number_of_contracts'})

        return {
            'total_amount': float(full_data['contract_amount'].sum()),
            'total_contracts': int(full_data.shape[0]),
            'by_manager': data_sales_by_managers.to_dict('records'),
            'by_source': data_sales_by_source.to_dict('records'),
            'by_type': type_contracts_data.to_dict('records')
        }


class FinmapService:
    """Service for working with Finmap API"""

    def __init__(self, api_key: str, company_id: str = ""):
        self.api_key = api_key
        self.company_id = company_id
        self.base_url = "https://api.finmap.online/v2.2"

    def get_income_for_date(self, target_date: str) -> Dict:
        """
        Get income operations for specific date
        Returns: {'total': float, 'count': int}
        """
        if not self.api_key:
            return {'total': 0.0, 'count': 0}

        try:
            # Parse date
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        kyiv = ZoneInfo("Europe/Kyiv")
        date_obj = datetime.fromisoformat(target_date)
        day_start = datetime.combine(date_obj.date(), datetime.min.time()).replace(tzinfo=kyiv)
        day_end = day_start + timedelta(days=1)

        start_ms = int(day_start.timestamp()) * 1000
        end_ms = int(day_end.timestamp()) * 1000

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "apiKey": self.api_key,
        }

        if self.company_id:
            headers["X-Company-Id"] = self.company_id

        limit = 100
        offset = 0
        use_alt_dates = False
        total = 0.0
        count = 0

        while True:
            body = {
                "limit": limit,
                "offset": offset,
                "useDateOfPayment": True,
                "approved": True,
                "types": ["income"],
                "desc": True,
                "field": "date",
            }

            if not use_alt_dates:
                body.update({"startDate": start_ms, "endDate": end_ms})
            else:
                body.update({"dateFrom": start_ms, "dateTo": end_ms})

            try:
                response = requests.post(
                    f"{self.base_url}/operations/list",
                    json=body,
                    headers=headers,
                    timeout=30
                )

                if response.status_code in (400, 422) and not use_alt_dates:
                    use_alt_dates = True
                    continue

                if not (200 <= response.status_code < 300):
                    return {'total': 0.0, 'count': 0}

                data = response.json()
                rows = data.get("list") or data.get("items") or []

                for item in rows:
                    amt = float(item.get("companyCurrencySum") or item.get("amount") or item.get("sum") or 0)
                    total += amt

                count += len(rows)

                if len(rows) < limit:
                    break

                offset += len(rows)

            except Exception as e:
                print(f"[Finmap Error] {str(e)}")
                return {'total': 0.0, 'count': 0}

        return {'total': total, 'count': count}
