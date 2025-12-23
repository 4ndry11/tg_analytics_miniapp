import React from 'react';
import './Plans.css';

export const Plans: React.FC = () => {
  return (
    <div className="plans">
      <header className="plans__header">
        <h1>🎯 План/Факт аналіз</h1>
      </header>

      <div className="plans__placeholder card">
        <div className="plans__placeholder-icon">📊</div>
        <h2>Розділ в розробці</h2>
        <p>Функціонал встановлення та відстеження планів буде доступний у наступній версії.</p>
        <p className="plans__placeholder-subtitle">
          Тут ви зможете:
        </p>
        <ul className="plans__features">
          <li>✅ Встановлювати плани продажів</li>
          <li>✅ Відстежувати виконання план/факт</li>
          <li>✅ Аналізувати відхилення</li>
          <li>✅ Прогнозувати результати</li>
        </ul>
      </div>
    </div>
  );
};
