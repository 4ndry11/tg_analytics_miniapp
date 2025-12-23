from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
from .b24_service import B24Service


def calculate_working_hours(start_time, end_time, work_start_hour=9, work_end_hour=21):
    """
    Calculate working hours between two dates, excluding night hours (21:00-09:00)
    All days are considered working days (including weekends)
    """
    if pd.isna(start_time) or pd.isna(end_time):
        return pd.NaT

    total_working_seconds = 0
    current_time = start_time

    while current_time < end_time:
        current_hour = current_time.hour

        if work_start_hour <= current_hour < work_end_hour:
            end_of_work_today = current_time.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)
            period_end = min(end_of_work_today, end_time)
            working_seconds = (period_end - current_time).total_seconds()
            total_working_seconds += working_seconds
            current_time = period_end
        else:
            if current_hour < work_start_hour:
                current_time = current_time.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)
            else:
                next_day = current_time + timedelta(days=1)
                current_time = next_day.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)

    return timedelta(seconds=total_working_seconds)


class LeadsService:
    """Service for working with leads data"""

    def __init__(self, domain: str, user_id: int, leads_token: str, users_token: str, status_token: str):
        self.b24_leads = B24Service(domain, user_id, leads_token)
        self.b24_users = B24Service(domain, user_id, users_token)
        self.b24_status = B24Service(domain, user_id, status_token)
        self.domain = domain

    def get_leads_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get leads data for date range"""
        leads = self.b24_leads.get_list(
            'crm.lead.list',
            b24_filter={
                '>=DATE_CREATE': f'{start_date}T00:00:01',
                '<=DATE_CREATE': f'{end_date}T23:59:59'
            },
            select=['ID', 'STATUS_ID', 'ASSIGNED_BY_ID', 'DATE_CREATE', 'UTM_SOURCE', 'UF_CRM_1745414446']
        )

        if not leads:
            return pd.DataFrame()

        leads_df = pd.DataFrame(leads)
        leads_df['DATE_CREATE'] = pd.to_datetime(leads_df['DATE_CREATE'])
        leads_df['taken_in_work'] = pd.to_datetime(leads_df['UF_CRM_1745414446'])
        leads_df = leads_df.drop('UF_CRM_1745414446', axis=1)

        # Calculate working time
        leads_df['time_taken_in_work'] = leads_df.apply(
            lambda row: calculate_working_hours(row['DATE_CREATE'], row['taken_in_work']),
            axis=1
        )

        return leads_df

    def get_users(self) -> pd.DataFrame:
        """Get users data"""
        users = self.b24_users.get_list('user.get', select=['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME'])
        users_df = pd.DataFrame(users)[['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME']]
        users_df['FULL_NAME'] = users_df[['NAME', 'LAST_NAME', 'SECOND_NAME']].fillna('').agg(' '.join, axis=1).str.strip()
        return users_df[['ID', 'FULL_NAME']]

    def get_statuses(self) -> pd.DataFrame:
        """Get lead statuses"""
        statuses = self.b24_status.get_list('crm.status.list', select=['ID', 'NAME'])
        df_status = pd.DataFrame(statuses)
        return df_status[['STATUS_ID', 'NAME']]

    def get_deals_data(self, start_date: str, end_date: str, category_id: int = 0) -> pd.DataFrame:
        """Get deals data for date range"""
        deal_filter = {
            "CATEGORY_ID": category_id,
            ">=CLOSEDATE": f'{start_date}T00:00:01',
            "<=CLOSEDATE": f'{end_date}T23:59:59',
            'STAGE_ID': 'WON'
        }

        select_fields = ["ID", "OPPORTUNITY", 'ASSIGNED_BY_ID', 'CLOSEDATE', 'UTM_SOURCE', 'UF_CRM_1695636781']
        deals = self.b24_leads.get_list("crm.deal.list", b24_filter=deal_filter, select=select_fields)

        if not deals:
            return pd.DataFrame()

        return pd.DataFrame(deals)

    def calculate_metrics(self, leads_df: pd.DataFrame, deals_df: pd.DataFrame, users_df: pd.DataFrame) -> Dict:
        """Calculate conversion metrics and reaction times"""
        # Filter leads with valid reaction time
        leads_with_time = leads_df[leads_df['time_taken_in_work'].notna()].copy()
        leads_with_time['time_in_seconds'] = leads_with_time['time_taken_in_work'].dt.total_seconds()

        # Trim outliers for department metrics (1%-95%)
        if len(leads_with_time) > 0:
            lower_bound = leads_with_time['time_in_seconds'].quantile(0.01)
            upper_bound = leads_with_time['time_in_seconds'].quantile(0.95)
            leads_trimmed = leads_with_time[
                (leads_with_time['time_in_seconds'] >= lower_bound) &
                (leads_with_time['time_in_seconds'] <= upper_bound)
            ].copy()
        else:
            leads_trimmed = leads_with_time.copy()

        # Aggregate leads by manager
        agg_leads = leads_df.groupby('ASSIGNED_BY_ID').agg({'ID': 'count'}).reset_index()
        agg_leads = agg_leads.rename(columns={'ID': 'number_of_leads'})

        # Add median reaction time per manager (without trimming)
        if len(leads_with_time) > 0:
            time_medians = leads_with_time.groupby('ASSIGNED_BY_ID')['time_taken_in_work'].median().reset_index()
            agg_leads = agg_leads.merge(time_medians, on='ASSIGNED_BY_ID', how='left')
        else:
            agg_leads['time_taken_in_work'] = pd.NaT

        # Aggregate deals
        if not deals_df.empty:
            agg_deals = deals_df.groupby('ASSIGNED_BY_ID').agg({'ID': 'count'}).reset_index()
            agg_deals = agg_deals.rename(columns={'ID': 'number_of_deals'})
        else:
            agg_deals = pd.DataFrame(columns=['ASSIGNED_BY_ID', 'number_of_deals'])
            agg_deals['ASSIGNED_BY_ID'] = leads_df['ASSIGNED_BY_ID'].unique()
            agg_deals['number_of_deals'] = 0

        # Merge leads and deals
        full_agg_data = agg_leads.merge(agg_deals, how='left', on='ASSIGNED_BY_ID')
        full_agg_data['number_of_deals'] = full_agg_data['number_of_deals'].fillna(0)

        # Calculate CR%
        full_agg_data['CR%'] = round(full_agg_data.number_of_deals / full_agg_data.number_of_leads * 100, 2)

        # Add user names
        full_agg_data = full_agg_data.merge(users_df, left_on='ASSIGNED_BY_ID', right_on='ID', how='left')

        # Department median (trimmed data)
        if len(leads_trimmed) > 0:
            dept_median = leads_trimmed['time_taken_in_work'].median()
        else:
            dept_median = pd.NaT

        return {
            'by_manager': full_agg_data.to_dict('records'),
            'department_median': dept_median,
            'total_leads': len(leads_df),
            'total_deals': len(deals_df) if not deals_df.empty else 0
        }

    def get_full_report(self, start_date: str, end_date: str) -> Dict:
        """Get full leads report with all analytics"""
        leads_df = self.get_leads_data(start_date, end_date)
        deals_df = self.get_deals_data(start_date, end_date)
        users_df = self.get_users()
        statuses_df = self.get_statuses()

        if leads_df.empty:
            return {
                'metrics': {'by_manager': [], 'department_median': None, 'total_leads': 0, 'total_deals': 0},
                'distribution': {},
                'leads_detail': []
            }

        # Calculate metrics
        metrics = self.calculate_metrics(leads_df, deals_df, users_df)

        # Distribution analysis
        leads_by_managers = leads_df.merge(users_df, left_on='ASSIGNED_BY_ID', right_on='ID', how='inner')
        full_data = leads_by_managers.merge(statuses_df, on='STATUS_ID', how='inner')
        full_data = full_data.drop_duplicates()[['ID_x', 'DATE_CREATE', 'UTM_SOURCE', 'FULL_NAME', 'NAME']]
        full_data = full_data.rename(columns={'ID_x': 'ID_lead', 'FULL_NAME': 'manager_name', 'NAME': 'status_lead'})

        distribution = {
            'by_source': full_data['UTM_SOURCE'].value_counts().to_dict(),
            'by_manager': full_data['manager_name'].value_counts().to_dict(),
            'by_status': full_data['status_lead'].value_counts().to_dict(),
            'heatmap': full_data.pivot_table(
                index='manager_name',
                columns='status_lead',
                values='ID_lead',
                aggfunc='count',
                fill_value=0
            ).to_dict()
        }

        # Leads detail for Excel export
        leads_detail = leads_df[['ID', 'ASSIGNED_BY_ID', 'DATE_CREATE', 'taken_in_work', 'time_taken_in_work']].copy()
        leads_detail = leads_detail.merge(users_df, left_on='ASSIGNED_BY_ID', right_on='ID', how='left')
        leads_detail['link'] = leads_detail['ID_x'].apply(lambda x: f'https://{self.domain}/crm/lead/details/{x}/')

        return {
            'metrics': metrics,
            'distribution': distribution,
            'leads_detail': leads_detail.to_dict('records')
        }
