import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format, subDays } from 'date-fns';
import { reportsApi } from '../services/api';
import { InteractiveChart } from '../components/InteractiveChart/InteractiveChart';
import './Sales.css';

export const Sales: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(
    format(subDays(new Date(), 1), 'yyyy-MM-dd')
  );

  const { data: report, isLoading } = useQuery({
    queryKey: ['daily-report', selectedDate],
    queryFn: () => reportsApi.getDaily(selectedDate),
  });

  if (isLoading) {
    return (
      <div className="sales">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const managerAmountData = report?.sales?.by_manager?.map((m: any) => ({
    name: m.manager,
    amount: m.contract_amount,
    contracts: m.number_of_contracts,
  })) || [];

  const sourceAmountData = report?.sales?.by_source?.map((s: any) => ({
    name: s.UTM_SOURCE,
    amount: s.contract_amount,
    contracts: s.number_of_contracts,
  })) || [];

  const typeData = report?.sales?.by_type?.map((t: any) => ({
    name: t.type_contract,
    amount: t.contract_amount,
    contracts: t.number_of_contracts,
  })) || [];

  return (
    <div className="sales">
      <header className="sales__header">
        <h1>💰 Аналітика по продажам</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="sales__date-picker"
        />
      </header>

      {/* Summary */}
      <div className="sales__summary card">
        <div className="sales__summary-main">
          <div className="sales__summary-label">Загальна сума</div>
          <div className="sales__summary-amount">
            {(report?.sales?.total_amount || 0).toLocaleString('uk-UA')} грн
          </div>
          <div className="sales__summary-contracts">
            Контрактів: {report?.sales?.total_contracts || 0}
          </div>
        </div>
      </div>

      {/* Finmap */}
      {report?.finmap && report.finmap.total > 0 && (
        <div className="sales__finmap card">
          <h3>💵 Фактичні надходження (Finmap)</h3>
          <div className="sales__finmap-amount">
            {report.finmap.total.toLocaleString('uk-UA', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}{' '}
            грн
          </div>
          <p className="sales__finmap-count">Операцій: {report.finmap.count}</p>
        </div>
      )}

      {/* Contract Types */}
      {typeData.length > 0 && (
        <div className="sales__types card">
          <h3>📄 По типах контрактів</h3>
          <div className="sales__types-grid">
            {typeData.map((type, index) => (
              <div key={index} className="sales__type-item">
                <div className="sales__type-name">{type.name}</div>
                <div className="sales__type-amount">
                  {type.amount.toLocaleString('uk-UA')} грн
                </div>
                <div className="sales__type-contracts">
                  Контрактів: {type.contracts}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Managers Chart */}
      <InteractiveChart
        data={managerAmountData}
        dataKey="amount"
        nameKey="name"
        title="👥 Продажі по менеджерам (сума)"
        color="#4CAF50"
      />

      {/* Sources Chart */}
      <InteractiveChart
        data={sourceAmountData}
        dataKey="amount"
        nameKey="name"
        title="📍 Продажі по джерелам (сума)"
        color="#FF9800"
      />

      {/* Managers Table */}
      <div className="sales__table card">
        <h3>📊 Детальна таблиця по менеджерам</h3>
        <div className="sales__table-scroll">
          <table className="sales__table-content">
            <thead>
              <tr>
                <th>Менеджер</th>
                <th>Сума</th>
                <th>Контракти</th>
              </tr>
            </thead>
            <tbody>
              {report?.sales?.by_manager?.map((manager: any, index: number) => (
                <tr key={index}>
                  <td>{manager.manager}</td>
                  <td className="sales__table-amount">
                    {manager.contract_amount.toLocaleString('uk-UA')} грн
                  </td>
                  <td className="sales__table-contracts">{manager.number_of_contracts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
