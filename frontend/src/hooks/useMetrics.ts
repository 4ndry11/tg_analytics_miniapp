import { useQuery } from '@tanstack/react-query';
import { reportsApi, metricsApi } from '../services/api';

export const useMetrics = (date?: string) => {
  return useQuery({
    queryKey: ['metrics', date],
    queryFn: () => reportsApi.getDaily(date),
    enabled: !!date,
  });
};

export const useLeadsMetrics = (date?: string, managerId?: string) => {
  return useQuery({
    queryKey: ['leads-metrics', date, managerId],
    queryFn: () => metricsApi.getLeads(date, managerId),
    enabled: !!date,
  });
};

export const useSalesMetrics = (date?: string, managerId?: string) => {
  return useQuery({
    queryKey: ['sales-metrics', date, managerId],
    queryFn: () => metricsApi.getSales(date, managerId),
    enabled: !!date,
  });
};

export const useConversionMetrics = (startDate: string, endDate: string) => {
  return useQuery({
    queryKey: ['conversion-metrics', startDate, endDate],
    queryFn: () => metricsApi.getConversion(startDate, endDate),
    enabled: !!startDate && !!endDate,
  });
};
