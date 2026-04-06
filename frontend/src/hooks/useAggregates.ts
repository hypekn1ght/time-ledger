import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';

export function useWeeklyAggregate(weekOffset = 0) {
  return useQuery({
    queryKey: ['weekly', weekOffset],
    queryFn: () => weekOffset === 0 ? api.getThisWeek() : api.getWeeklyOffset(weekOffset),
    refetchInterval: 1000 * 60, // Refresh every minute
  });
}

export function useSync() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.triggerSync,
    onSuccess: () => {
      // After sync, invalidate all related queries
      queryClient.invalidateQueries({ queryKey: ['calendars'] });
      queryClient.invalidateQueries({ queryKey: ['weekly'] });
      queryClient.invalidateQueries({ queryKey: ['sync'] });
    },
  });
}

export function useSyncStatus() {
  return useQuery({
    queryKey: ['sync'],
    queryFn: api.getSyncStatus,
    refetchInterval: 2000, // Poll every 2s during sync
  });
}
