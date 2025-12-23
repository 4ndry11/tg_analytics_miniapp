import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format, subDays } from 'date-fns';
import { reportsApi } from '../services/api';
import { MetricCard } from '../components/MetricCard/MetricCard';
import { AlertBanner } from '../components/AlertBanner/AlertBanner';
import './Home.css';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<string>(
    format(subDays(new Date(), 1), 'yyyy-MM-dd')
  );

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['daily-report', selectedDate],
    queryFn: () => reportsApi.getDaily(selectedDate),
  });

  const formatTime = (time: string | null) => {
    if (!time) return 'N/A';
    return time;
  };

  if (isLoading) {
    return (
      <div className="home">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home">
        <div className="error">
          Помилка завантаження даних. Спробуйте пізніше.
        </div>
      </div>
    );
  }

  const totalCR = report?.leads?.metrics?.total_leads && report?.leads?.metrics?.total_deals
    ? ((report.leads.metrics.total_deals / report.leads.metrics.total_leads) * 100).toFixed(2)
    : '0.00';

  return (
    <div className="home">
      <header className="home__header">
        <h1>Аналітика</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="home__date-picker"
        />
      </header>

      {/* Alerts */}
      {report?.alerts && report.alerts.length > 0 && (
        <AlertBanner alerts={report.alerts} />
      )}

      {/* KPI Cards */}
      <div className="home__kpi-grid">
        <MetricCard
          title="Ліди"
          value={report?.leads?.metrics?.total_leads || 0}
          icon="🎯"
          onClick={() => navigate('/leads')}
          subtitle={`Джерел: ${Object.keys(report?.leads?.distribution?.by_source || {}).length}`}
        />

        <MetricCard
          title="Продажі"
          value={report?.sales?.total_contracts || 0}
          icon="💰"
          onClick={() => navigate('/sales')}
          subtitle={`${(report?.sales?.total_amount || 0).toLocaleString('uk-UA')} грн`}
          highlighted
        />

        <MetricCard
          title="CR%"
          value={`${totalCR}%`}
          icon="📈"
          trend={parseFloat(totalCR) > 20 ? 'up' : parseFloat(totalCR) > 10 ? 'neutral' : 'down'}
          trendValue={`${report?.leads?.metrics?.total_deals || 0} з ${report?.leads?.metrics?.total_leads || 0}`}
        />
      </div>

      {/* Department Metrics */}
      <div className="home__department">
        <div className="card">
          <h2>Час реакції відділу</h2>
          <div className="home__department-time">
            {formatTime(report?.leads?.metrics?.department_median || null)}
          </div>
          <p className="home__department-subtitle">Медіана по відділу</p>
        </div>
      </div>

      {/* Finmap */}
      {report?.finmap && report.finmap.total > 0 && (
        <div className="home__finmap card">
          <h3>💵 Фактичні надходження (Finmap)</h3>
          <div className="home__finmap-amount">
            {report.finmap.total.toLocaleString('uk-UA', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}{' '}
            грн
          </div>
          <p className="home__finmap-count">Операцій: {report.finmap.count}</p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="home__actions">
        <button onClick={() => navigate('/leads')} className="home__action-btn">
          📊 Детально по лідам
        </button>
        <button onClick={() => navigate('/sales')} className="home__action-btn">
          💼 Детально по продажам
        </button>
      </div>
    </div>
  );
};
