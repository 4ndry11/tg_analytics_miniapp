import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { format, subDays } from 'date-fns';
import { metricsApi } from '../services/api';
import './ManagerDetail.css';

export const ManagerDetail: React.FC = () => {
  const { managerId } = useParams<{ managerId: string }>();
  const navigate = useNavigate();

  const startDate = format(subDays(new Date(), 7), 'yyyy-MM-dd');
  const endDate = format(new Date(), 'yyyy-MM-dd');

  const { data, isLoading } = useQuery({
    queryKey: ['manager-detail', managerId, startDate, endDate],
    queryFn: () => metricsApi.getManagerDetail(managerId!, startDate, endDate),
    enabled: !!managerId,
  });

  if (isLoading) {
    return (
      <div className="manager-detail">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="manager-detail">
      <header className="manager-detail__header">
        <button onClick={() => navigate(-1)} className="manager-detail__back">
          ← Назад
        </button>
        <h1>👤 {data?.manager_name}</h1>
      </header>

      <div className="manager-detail__summary card">
        <div className="manager-detail__stat">
          <span className="manager-detail__stat-label">Ліди:</span>
          <span className="manager-detail__stat-value">{data?.total_leads || 0}</span>
        </div>

        <div className="manager-detail__stat">
          <span className="manager-detail__stat-label">Продажі:</span>
          <span className="manager-detail__stat-value">{data?.total_deals || 0}</span>
        </div>

        <div className="manager-detail__stat">
          <span className="manager-detail__stat-label">CR%:</span>
          <span className="manager-detail__stat-value">{data?.cr_percent}%</span>
        </div>

        <div className="manager-detail__stat">
          <span className="manager-detail__stat-label">Час реакції:</span>
          <span className="manager-detail__stat-value">
            {data?.avg_reaction_time || 'N/A'}
          </span>
        </div>
      </div>

      <div className="manager-detail__content card">
        <h3>Деталі за період</h3>
        <p>
          {startDate} - {endDate}
        </p>
      </div>
    </div>
  );
};
