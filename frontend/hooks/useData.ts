'use client';

/**
 * Custom hooks for data fetching from the API.
 *
 * These hooks provide a clean abstraction for fetching data while managing
 * loading, error, and caching states automatically.
 */

import { useAsync } from './useAsync';
import { useCallback, useEffect } from 'react';
import { patientsApi, doctorsApi, appointmentsApi } from '@/lib/api';

/**
 * Hook for fetching a single patient.
 *
 * @param patientId The patient ID to fetch
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Patient data, loading state, and error
 */
export function usePatient(patientId: number | null, autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const fetch = useCallback(async () => {
    if (!patientId) return;
    return execute(() => patientsApi.get(patientId));
  }, [patientId, execute]);

  useEffect(() => {
    if (autoFetch && patientId) {
      fetch();
    }
  }, [patientId, autoFetch, fetch]);

  return { patient: data, loading, error, refetch: fetch, reset };
}

/**
 * Hook for fetching a list of patients with search.
 *
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Patients list, loading state, and error
 */
export function usePatients(autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const list = useCallback(
    (skip = 0, limit = 100) => execute(() => patientsApi.list(skip, limit)),
    [execute]
  );

  const search = useCallback(
    (query: string, skip = 0, limit = 100) => {
      if (!query.trim()) return list(skip, limit);
      // Note: API doesn't have separate search endpoint, this would be client-side or API enhanced
      return execute(() => patientsApi.list(skip, limit));
    },
    [execute, list]
  );

  useEffect(() => {
    if (autoFetch) {
      list();
    }
  }, [autoFetch, list]);

  return { patients: data || [], loading, error, list, search, reset };
}

/**
 * Hook for fetching a single doctor.
 *
 * @param doctorId The doctor ID to fetch
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Doctor data, loading state, and error
 */
export function useDoctor(doctorId: number | null, autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const fetch = useCallback(async () => {
    if (!doctorId) return;
    return execute(() => doctorsApi.get(doctorId));
  }, [doctorId, execute]);

  useEffect(() => {
    if (autoFetch && doctorId) {
      fetch();
    }
  }, [doctorId, autoFetch, fetch]);

  return { doctor: data, loading, error, refetch: fetch, reset };
}

/**
 * Hook for fetching a list of doctors with optional filtering.
 *
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Doctors list, loading state, and error
 */
export function useDoctors(autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const list = useCallback(
    (skip = 0, limit = 100) => execute(() => doctorsApi.list(skip, limit)),
    [execute]
  );

  useEffect(() => {
    if (autoFetch) {
      list();
    }
  }, [autoFetch, list]);

  return { doctors: data || [], loading, error, list, reset };
}

/**
 * Hook for fetching a single appointment.
 *
 * @param appointmentId The appointment ID to fetch
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Appointment data, loading state, and error
 */
export function useAppointment(appointmentId: number | null, autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const fetch = useCallback(async () => {
    if (!appointmentId) return;
    return execute(() => appointmentsApi.get(appointmentId));
  }, [appointmentId, execute]);

  useEffect(() => {
    if (autoFetch && appointmentId) {
      fetch();
    }
  }, [appointmentId, autoFetch, fetch]);

  return { appointment: data, loading, error, refetch: fetch, reset };
}

/**
 * Hook for fetching a list of appointments.
 *
 * @param autoFetch Whether to fetch automatically on mount
 * @returns Appointments list, loading state, and error
 */
export function useAppointments(autoFetch = true) {
  const { data, loading, error, execute, reset } = useAsync();

  const list = useCallback(
    (skip = 0, limit = 100) => execute(() => appointmentsApi.list(skip, limit)),
    [execute]
  );

  useEffect(() => {
    if (autoFetch) {
      list();
    }
  }, [autoFetch, list]);

  return { appointments: data || [], loading, error, list, reset };
}

/**
 * Hook for handling API mutations (create, update, delete).
 *
 * @param operation The async operation to perform
 * @returns Mutation state and execute function
 */
export function useMutation<D = any>(operation: (data: D) => Promise<any>) {
  const { data, loading, error, execute, reset } = useAsync();

  const mutate = useCallback(
    (mutationData: D) => execute(() => operation(mutationData)),
    [execute, operation]
  );

  return { data, loading, error, mutate, reset };
}

/**
 * Hook for optimistic updates.
 *
 * Immediately updates the UI while the API request is in flight,
 * rolling back if the request fails.
 *
 * @template T The item type
 * @param items Current list of items
 * @param onUpdate Callback to update item
 * @param onError Callback on error
 * @returns Optimistic update function
 */
export function useOptimisticUpdate<T extends { id: number | string }>(
  items: T[],
  onUpdate: (items: T[]) => void,
  onError: (error: string) => void
) {
  return useCallback(
    async (itemId: number | string, updates: Partial<T>, apiCall: () => Promise<void>) => {
      // Find original item
      const originalItem = items.find((item) => item.id === itemId);
      if (!originalItem) return;

      // Optimistically update UI
      const updatedItems = items.map((item) =>
        item.id === itemId ? { ...item, ...updates } : item
      );
      onUpdate(updatedItems);

      // Try to update via API
      try {
        await apiCall();
      } catch (err: any) {
        // Rollback to original state
        onUpdate(items);
        onError(err?.message || 'Update failed');
      }
    },
    [items, onUpdate, onError]
  );
}
