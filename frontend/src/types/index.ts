export interface Manager {
  ASSIGNED_BY_ID: string;
  FULL_NAME: string;
  'CR%': number;
  number_of_leads: number;
  number_of_deals: number;
  time_taken_in_work?: string;
}

export interface LeadsMetrics {
  by_manager: Manager[];
  department_median: string | null;
  total_leads: number;
  total_deals: number;
}

export interface LeadsDistribution {
  by_source: Record<string, number>;
  by_manager: Record<string, number>;
  by_status: Record<string, number>;
  heatmap: Record<string, Record<string, number>>;
}

export interface LeadsReport {
  metrics: LeadsMetrics;
  distribution: LeadsDistribution;
  leads_detail: any[];
}

export interface SalesByManager {
  manager: string;
  contract_amount: number;
  number_of_contracts: number;
}

export interface SalesBySource {
  UTM_SOURCE: string;
  contract_amount: number;
  number_of_contracts: number;
}

export interface SalesByType {
  type_contract: string;
  contract_amount: number;
  number_of_contracts: number;
}

export interface SalesReport {
  total_amount: number;
  total_contracts: number;
  by_manager: SalesByManager[];
  by_source: SalesBySource[];
  by_type: SalesByType[];
}

export interface FinmapData {
  total: number;
  count: number;
}

export interface Alert {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  value?: number;
  threshold?: number;
  manager_name?: string;
  timestamp: string;
}

export interface DailyReport {
  date: string;
  period: 'daily';
  leads: LeadsReport;
  sales: SalesReport;
  finmap: FinmapData;
  alerts: Alert[];
}

export interface WeeklyReport {
  start_date: string;
  end_date: string;
  period: 'weekly';
  leads: LeadsReport;
  sales: SalesReport;
}

export interface MonthlyReport {
  year: number;
  month: number;
  start_date: string;
  end_date: string;
  period: 'monthly';
  leads: LeadsReport;
  sales: SalesReport;
}

export type PeriodType = 'daily' | 'weekly' | 'monthly' | 'custom';

export interface DateRange {
  start: string;
  end: string;
}
