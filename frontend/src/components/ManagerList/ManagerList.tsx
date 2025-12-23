import React from 'react';
import type { Manager } from '../../types';
import './ManagerList.css';

interface ManagerListProps {
  managers: Manager[];
  onManagerClick?: (managerId: string) => void;
}

export const ManagerList: React.FC<ManagerListProps> = ({ managers, onManagerClick }) => {
  const formatTime = (time: any) => {
    if (!time) return 'N/A';
    return String(time);
  };

  return (
    <div className="manager-list">
      {managers.map((manager, index) => (
        <div
          key={index}
          className="manager-list__item"
          onClick={() => onManagerClick?.(manager.ASSIGNED_BY_ID)}
        >
          <div className="manager-list__header">
            <span className="manager-list__name">👤 {manager.FULL_NAME}</span>
            <span
              className={`manager-list__cr ${
                manager['CR%'] < 10 ? 'manager-list__cr--low' : ''
              }`}
            >
              CR: {manager['CR%'].toFixed(2)}%
            </span>
          </div>

          <div className="manager-list__stats">
            <div className="manager-list__stat">
              <span className="manager-list__stat-label">Ліди:</span>
              <span className="manager-list__stat-value">{manager.number_of_leads}</span>
            </div>

            <div className="manager-list__stat">
              <span className="manager-list__stat-label">Продажі:</span>
              <span className="manager-list__stat-value">{manager.number_of_deals}</span>
            </div>

            <div className="manager-list__stat">
              <span className="manager-list__stat-label">Час реакції:</span>
              <span className="manager-list__stat-value">
                {formatTime(manager.time_taken_in_work)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
