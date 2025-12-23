import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import './InteractiveChart.css';

interface InteractiveChartProps {
  data: any[];
  dataKey: string;
  nameKey: string;
  title?: string;
  color?: string;
  onBarClick?: (data: any) => void;
  height?: number;
}

export const InteractiveChart: React.FC<InteractiveChartProps> = ({
  data,
  dataKey,
  nameKey,
  title,
  color = '#4A90E2',
  onBarClick,
  height = 300,
}) => {
  const [activeIndex, setActiveIndex] = React.useState<number | null>(null);

  const handleBarClick = (data: any, index: number) => {
    setActiveIndex(index);
    if (onBarClick) {
      onBarClick(data);
    }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="interactive-chart__tooltip">
          <p className="interactive-chart__tooltip-label">{payload[0].payload[nameKey]}</p>
          <p className="interactive-chart__tooltip-value">
            {payload[0].value.toLocaleString('uk-UA')}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="interactive-chart">
      {title && <h3 className="interactive-chart__title">{title}</h3>}

      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: 10, bottom: 40 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
          <XAxis
            dataKey={nameKey}
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#78909C', fontSize: 12 }}
          />
          <YAxis tick={{ fill: '#78909C', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(74, 144, 226, 0.1)' }} />
          <Bar
            dataKey={dataKey}
            onClick={handleBarClick}
            cursor="pointer"
            radius={[8, 8, 0, 0]}
          >
            {data.map((_entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={activeIndex === index ? '#2196F3' : color}
                opacity={activeIndex === null || activeIndex === index ? 1 : 0.6}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {onBarClick && (
        <div className="interactive-chart__hint">
          Натисніть на стовпчик для деталізації
        </div>
      )}
    </div>
  );
};
