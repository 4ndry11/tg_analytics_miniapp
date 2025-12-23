import React from 'react';
import './MetricCard.css';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  onClick?: () => void;
  highlighted?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
  onClick,
  highlighted = false,
}) => {
  const getTrendClass = () => {
    if (!trend) return '';
    return `metric-card__trend--${trend}`;
  };

  return (
    <div
      className={`metric-card ${highlighted ? 'metric-card--highlighted' : ''} ${
        onClick ? 'metric-card--clickable' : ''
      }`}
      onClick={onClick}
    >
      {icon && <div className="metric-card__icon">{icon}</div>}

      <div className="metric-card__content">
        <div className="metric-card__title">{title}</div>
        <div className="metric-card__value">{value}</div>

        {subtitle && <div className="metric-card__subtitle">{subtitle}</div>}

        {trend && trendValue && (
          <div className={`metric-card__trend ${getTrendClass()}`}>
            <span className="metric-card__trend-icon">
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
            </span>
            {trendValue}
          </div>
        )}
      </div>
    </div>
  );
};
