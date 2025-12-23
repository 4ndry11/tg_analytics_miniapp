import React from 'react';
import './DatePicker.css';

interface DatePickerProps {
  value: string;
  onChange: (date: string) => void;
  label?: string;
}

export const DatePicker: React.FC<DatePickerProps> = ({ value, onChange, label }) => {
  return (
    <div className="date-picker">
      {label && <label className="date-picker__label">{label}</label>}
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="date-picker__input"
      />
    </div>
  );
};
