import React from 'react';
import type { Alert } from '../../types';
import './AlertBanner.css';

interface AlertBannerProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alerts, onAlertClick }) => {
  if (!alerts || alerts.length === 0) {
    return null;
  }

  const getIconForSeverity = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return '🔴';
      case 'warning':
        return '🟡';
      case 'info':
        return '🔵';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="alert-banner">
      <div className="alert-banner__header">
        <h3>⚠️ Алерти</h3>
        <span className="alert-banner__count">{alerts.length}</span>
      </div>

      <div className="alert-banner__list">
        {alerts.map((alert, index) => (
          <div
            key={index}
            className={`alert-banner__item alert-banner__item--${alert.severity}`}
            onClick={() => onAlertClick?.(alert)}
          >
            <div className="alert-banner__item-icon">
              {getIconForSeverity(alert.severity)}
            </div>

            <div className="alert-banner__item-content">
              <div className="alert-banner__item-title">{alert.title}</div>
              <div className="alert-banner__item-description">{alert.description}</div>
              {alert.manager_name && (
                <div className="alert-banner__item-manager">
                  👤 {alert.manager_name}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
