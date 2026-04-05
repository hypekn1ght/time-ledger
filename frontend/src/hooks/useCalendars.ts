import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';

export function useCalendars() {
  return useQuery({
    queryKey: ['calendars'],
    queryFn: api.listCalendars,
    refetchInterval: false,
  });
}

export function useAddCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.addCalendar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendars'] });
    },
  });
}

export function useUpdateTier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, tier }: { id: number; tier: string }) =>
      api.updateTier(id, tier),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendars'] });
      queryClient.invalidateQueries({ queryKey: ['weekly'] });
    },
  });
}

export function useDeleteCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteCalendar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendars'] });
    },
  });
}
