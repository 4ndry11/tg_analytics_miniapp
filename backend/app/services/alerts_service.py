from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import pandas as pd


class AlertSeverity(str, Enum):
    CRITICAL = "critical"  # 🔴
    WARNING = "warning"  # 🟡
    INFO = "info"  # 🔵


class AlertType(str, Enum):
    CONVERSION_DROP = "conversion_drop"
    LOW_LEADS = "low_leads"
    SLOW_REACTION = "slow_reaction"
    NO_SALES = "no_sales"
    PLAN_MISS = "plan_miss"


class Alert:
    def __init__(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        value: float = None,
        threshold: float = None,
        manager_name: str = None
    ):
        self.type = alert_type
        self.severity = severity
        self.title = title
        self.description = description
        self.value = value
        self.threshold = threshold
        self.manager_name = manager_name
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'type': self.type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'threshold': self.threshold,
            'manager_name': self.manager_name,
            'timestamp': self.timestamp
        }


class AlertsService:
    """Service for generating alerts based on metrics"""

    # Thresholds configuration
    THRESHOLDS = {
        'conversion_drop_pct': 15,  # CR% drop by 15%
        'low_leads_pct': -20,  # 20% fewer leads
        'slow_reaction_seconds': 1200,  # > 20 minutes
        'plan_miss_pct': -10,  # Plan miss by 10%
        'min_conversion': 10.0,  # Minimum acceptable CR%
    }

    def __init__(self):
        self.alerts: List[Alert] = []

    def check_conversion_alerts(self, current_metrics: List[Dict], previous_metrics: List[Dict] = None) -> List[Alert]:
        """Check for conversion rate issues"""
        alerts = []

        for manager in current_metrics:
            cr = manager.get('CR%', 0)
            manager_name = manager.get('FULL_NAME', 'Unknown')

            # Critical: Very low conversion
            if cr < self.THRESHOLDS['min_conversion']:
                alerts.append(Alert(
                    alert_type=AlertType.CONVERSION_DROP,
                    severity=AlertSeverity.CRITICAL,
                    title=f"Критично низька конверсія",
                    description=f"{manager_name}: CR% = {cr:.2f}% (поріг: {self.THRESHOLDS['min_conversion']}%)",
                    value=cr,
                    threshold=self.THRESHOLDS['min_conversion'],
                    manager_name=manager_name
                ))

            # Warning: Conversion drop compared to previous period
            if previous_metrics:
                prev_manager = next((m for m in previous_metrics if m.get('FULL_NAME') == manager_name), None)
                if prev_manager:
                    prev_cr = prev_manager.get('CR%', 0)
                    if prev_cr > 0:
                        drop_pct = ((cr - prev_cr) / prev_cr) * 100
                        if drop_pct < -self.THRESHOLDS['conversion_drop_pct']:
                            alerts.append(Alert(
                                alert_type=AlertType.CONVERSION_DROP,
                                severity=AlertSeverity.WARNING,
                                title=f"Падіння конверсії",
                                description=f"{manager_name}: CR% впав на {abs(drop_pct):.1f}% (було {prev_cr:.2f}%, стало {cr:.2f}%)",
                                value=drop_pct,
                                threshold=-self.THRESHOLDS['conversion_drop_pct'],
                                manager_name=manager_name
                            ))

        return alerts

    def check_reaction_time_alerts(self, metrics: List[Dict]) -> List[Alert]:
        """Check for slow reaction time"""
        alerts = []

        for manager in metrics:
            reaction_time = manager.get('time_taken_in_work')
            manager_name = manager.get('FULL_NAME', 'Unknown')

            if reaction_time and not pd.isna(reaction_time):
                # Convert timedelta to seconds
                if isinstance(reaction_time, pd.Timedelta):
                    reaction_seconds = reaction_time.total_seconds()
                elif isinstance(reaction_time, timedelta):
                    reaction_seconds = reaction_time.total_seconds()
                else:
                    continue

                if reaction_seconds > self.THRESHOLDS['slow_reaction_seconds']:
                    hours = int(reaction_seconds // 3600)
                    minutes = int((reaction_seconds % 3600) // 60)

                    alerts.append(Alert(
                        alert_type=AlertType.SLOW_REACTION,
                        severity=AlertSeverity.WARNING,
                        title=f"Повільна реакція",
                        description=f"{manager_name}: середній час реакції {hours:02d}:{minutes:02d} (поріг: 20 хв)",
                        value=reaction_seconds,
                        threshold=self.THRESHOLDS['slow_reaction_seconds'],
                        manager_name=manager_name
                    ))

        return alerts

    def check_leads_volume_alerts(self, current_total: int, previous_total: int = None) -> List[Alert]:
        """Check for low leads volume"""
        alerts = []

        if previous_total and previous_total > 0:
            change_pct = ((current_total - previous_total) / previous_total) * 100

            if change_pct < self.THRESHOLDS['low_leads_pct']:
                alerts.append(Alert(
                    alert_type=AlertType.LOW_LEADS,
                    severity=AlertSeverity.WARNING,
                    title=f"Зниження кількості лідів",
                    description=f"Лідів на {abs(change_pct):.1f}% менше ніж вчора (було {previous_total}, стало {current_total})",
                    value=change_pct,
                    threshold=self.THRESHOLDS['low_leads_pct']
                ))

        return alerts

    def check_sales_alerts(self, total_contracts: int, total_amount: float) -> List[Alert]:
        """Check for sales issues"""
        alerts = []

        if total_contracts == 0:
            alerts.append(Alert(
                alert_type=AlertType.NO_SALES,
                severity=AlertSeverity.CRITICAL,
                title=f"Немає продажів",
                description=f"За вчорашній день не було жодної продажі!",
                value=0,
                threshold=1
            ))

        return alerts

    def check_plan_alerts(self, actual: float, planned: float, metric_name: str) -> List[Alert]:
        """Check plan vs actual performance"""
        alerts = []

        if planned > 0:
            deviation_pct = ((actual - planned) / planned) * 100

            if deviation_pct < self.THRESHOLDS['plan_miss_pct']:
                alerts.append(Alert(
                    alert_type=AlertType.PLAN_MISS,
                    severity=AlertSeverity.WARNING if deviation_pct > -30 else AlertSeverity.CRITICAL,
                    title=f"План не виконано: {metric_name}",
                    description=f"План: {planned:.0f}, Факт: {actual:.0f} ({deviation_pct:+.1f}%)",
                    value=deviation_pct,
                    threshold=self.THRESHOLDS['plan_miss_pct']
                ))

        return alerts

    def get_all_alerts(
        self,
        current_leads_metrics: Dict,
        current_sales_metrics: Dict,
        previous_leads_metrics: Dict = None,
        plans: List[Dict] = None
    ) -> List[Dict]:
        """Generate all alerts for current period"""
        all_alerts = []

        # Conversion alerts
        if current_leads_metrics.get('metrics', {}).get('by_manager'):
            prev_managers = None
            if previous_leads_metrics and previous_leads_metrics.get('metrics', {}).get('by_manager'):
                prev_managers = previous_leads_metrics['metrics']['by_manager']

            all_alerts.extend(
                self.check_conversion_alerts(
                    current_leads_metrics['metrics']['by_manager'],
                    prev_managers
                )
            )

            # Reaction time alerts
            all_alerts.extend(
                self.check_reaction_time_alerts(current_leads_metrics['metrics']['by_manager'])
            )

        # Leads volume alerts
        current_leads_total = current_leads_metrics.get('metrics', {}).get('total_leads', 0)
        if previous_leads_metrics:
            prev_leads_total = previous_leads_metrics.get('metrics', {}).get('total_leads', 0)
            all_alerts.extend(self.check_leads_volume_alerts(current_leads_total, prev_leads_total))

        # Sales alerts
        all_alerts.extend(
            self.check_sales_alerts(
                current_sales_metrics.get('total_contracts', 0),
                current_sales_metrics.get('total_amount', 0)
            )
        )

        # Plan alerts (if plans are provided)
        if plans:
            for plan in plans:
                metric_name = plan.get('metric_name', 'Unknown')
                planned_value = plan.get('planned_value', 0)
                actual_value = plan.get('actual_value', 0)
                all_alerts.extend(self.check_plan_alerts(actual_value, planned_value, metric_name))

        return [alert.to_dict() for alert in all_alerts]
