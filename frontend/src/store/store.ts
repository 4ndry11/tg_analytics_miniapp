import { create } from 'zustand';
import type { PeriodType, DateRange } from '../types';

interface AppState {
  // Date selection
  selectedDate: string;
  selectedPeriod: PeriodType;
  dateRange: DateRange;

  // UI state
  isLoading: boolean;
  error: string | null;

  // Actions
  setSelectedDate: (date: string) => void;
  setSelectedPeriod: (period: PeriodType) => void;
  setDateRange: (range: DateRange) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  selectedDate: new Date().toISOString().split('T')[0],
  selectedPeriod: 'daily',
  dateRange: {
    start: new Date().toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  },
  isLoading: false,
  error: null,

  // Actions
  setSelectedDate: (date) => set({ selectedDate: date }),
  setSelectedPeriod: (period) => set({ selectedPeriod: period }),
  setDateRange: (range) => set({ dateRange: range }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
