import axios from 'axios';
import type { DailyReport, WeeklyReport, MonthlyReport } from '../types';

// API base URL - change this to your deployed backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const reportsApi = {
  // Get daily report
  getDaily: async (date?: string): Promise<DailyReport> => {
    const params = date ? { date } : {};
    const response = await api.get('/api/reports/daily', { params });
    return response.data;
  },

  // Get weekly report
  getWeekly: async (startDate?: string, endDate?: string): Promise<WeeklyReport> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get('/api/reports/weekly', { params });
    return response.data;
  },

  // Get monthly report
  getMonthly: async (year?: number, month?: number): Promise<MonthlyReport> => {
    const params: any = {};
    if (year) params.year = year;
    if (month) params.month = month;
    const response = await api.get('/api/reports/monthly', { params });
    return response.data;
  },

  // Get custom period report
  getCustom: async (startDate: string, endDate: string) => {
    const response = await api.get('/api/reports/custom', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
};

export const metricsApi = {
  // Get leads metrics
  getLeads: async (date?: string, managerId?: string) => {
    const params: any = {};
    if (date) params.date = date;
    if (managerId) params.manager_id = managerId;
    const response = await api.get('/api/metrics/leads', { params });
    return response.data;
  },

  // Get sales metrics
  getSales: async (date?: string, managerId?: string) => {
    const params: any = {};
    if (date) params.date = date;
    if (managerId) params.manager_id = managerId;
    const response = await api.get('/api/metrics/sales', { params });
    return response.data;
  },

  // Get conversion metrics
  getConversion: async (startDate: string, endDate: string) => {
    const response = await api.get('/api/metrics/conversion', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get manager detail
  getManagerDetail: async (managerId: string, startDate: string, endDate: string) => {
    const response = await api.get(`/api/metrics/manager/${managerId}`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
};

export default api;
