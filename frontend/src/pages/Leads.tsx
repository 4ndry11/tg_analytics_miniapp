import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format, subDays } from 'date-fns';
import { reportsApi } from '../services/api';
import { InteractiveChart } from '../components/InteractiveChart/InteractiveChart';
import './Leads.css';

export const Leads: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(
    format(subDays(new Date(), 1), 'yyyy-MM-dd')
  );
  const [selectedManager, setSelectedManager] = useState<string | null>(null);

  const { data: report, isLoading } = useQuery({
    queryKey: ['daily-report', selectedDate],
    queryFn: () => reportsApi.getDaily(selectedDate),
  });

  if (isLoading) {
    return (
      <div className="leads">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const sourceData = Object.entries(report?.leads?.distribution?.by_source || {}).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  const managerData = report?.leads?.metrics?.by_manager?.map((m: any) => ({
    name: m.FULL_NAME,
    leads: m.number_of_leads,
    deals: m.number_of_deals,
    cr: m['CR%'],
  })) || [];

  const statusData = Object.entries(report?.leads?.distribution?.by_status || {}).map(
    ([name, value]) => ({
      name,
      value,
    })
  );

  const handleManagerClick = (data: any) => {
    setSelectedManager(data.name);
  };

  const selectedManagerData = report?.leads?.metrics?.by_manager?.find(
    (m: any) => m.FULL_NAME === selectedManager
  );

  return (
    <div className="leads">
      <header className="leads__header">
        <h1>🎯 Аналітика по лідам</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="leads__date-picker"
        />
      </header>

      {/* Summary */}
      <div className="leads__summary card">
        <div className="leads__summary-item">
          <span className="leads__summary-label">Всього лідів:</span>
          <span className="leads__summary-value">{report?.leads?.metrics?.total_leads || 0}</span>
        </div>
        <div className="leads__summary-item">
          <span className="leads__summary-label">Продажі:</span>
          <span className="leads__summary-value">{report?.leads?.metrics?.total_deals || 0}</span>
        </div>
        <div className="leads__summary-item">
          <span className="leads__summary-label">Час реакції:</span>
          <span className="leads__summary-value">
            {report?.leads?.metrics?.department_median || 'N/A'}
          </span>
        </div>
      </div>

      {/* Sources Chart */}
      <InteractiveChart
        data={sourceData}
        dataKey="value"
        nameKey="name"
        title="📍 Розподіл по джерелах (UTM_SOURCE)"
        color="#4A90E2"
      />

      {/* Managers Chart with Drill-Down */}
      <InteractiveChart
        data={managerData}
        dataKey="leads"
        nameKey="name"
        title="👥 Ліди по менеджерам (клікніть для деталей)"
        color="#2196F3"
        onBarClick={handleManagerClick}
      />

      {/* Manager Detail Modal */}
      {selectedManager && selectedManagerData && (
        <div className="leads__manager-detail">
          <div className="leads__manager-detail-header">
            <h3>👤 {selectedManager}</h3>
            <button
              className="leads__close-btn"
              onClick={() => setSelectedManager(null)}
            >
              ✕
            </button>
          </div>

          <div className="leads__manager-stats">
            <div className="leads__manager-stat">
              <span className="leads__manager-stat-label">Ліди:</span>
              <span className="leads__manager-stat-value">
                {selectedManagerData.number_of_leads}
              </span>
            </div>
            <div className="leads__manager-stat">
              <span className="leads__manager-stat-label">Продажі:</span>
              <span className="leads__manager-stat-value">
                {selectedManagerData.number_of_deals}
              </span>
            </div>
            <div className="leads__manager-stat">
              <span className="leads__manager-stat-label">CR%:</span>
              <span className="leads__manager-stat-value">
                {selectedManagerData['CR%'].toFixed(2)}%
              </span>
            </div>
            <div className="leads__manager-stat">
              <span className="leads__manager-stat-label">Час реакції:</span>
              <span className="leads__manager-stat-value">
                {selectedManagerData.time_taken_in_work || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Statuses Chart */}
      <InteractiveChart
        data={statusData}
        dataKey="value"
        nameKey="name"
        title="📋 Розподіл по стадіям"
        color="#4CAF50"
      />
    </div>
  );
};
