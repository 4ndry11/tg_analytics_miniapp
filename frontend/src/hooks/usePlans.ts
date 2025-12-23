import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

// Plans API endpoints (stub for future implementation)
const plansApi = {
  getAll: async () => {
    const response = await api.get('/api/plans/');
    return response.data;
  },

  create: async (plan: any) => {
    const response = await api.post('/api/plans/', plan);
    return response.data;
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/api/plans/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/api/plans/${id}`);
    return response.data;
  },
};

export const usePlans = () => {
  return useQuery({
    queryKey: ['plans'],
    queryFn: plansApi.getAll,
  });
};

export const useCreatePlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: plansApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
};

export const useUpdatePlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      plansApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
};

export const useDeletePlan = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: plansApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
};
