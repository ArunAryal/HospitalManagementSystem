'use client';

/**
 * Custom hooks for data fetching and state management.
 *
 * This module provides reusable hooks for common data fetching patterns,
 * reducing code duplication and improving maintainability.
 */

import { useState, useCallback, useEffect, useRef } from 'react';

export interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface UseAsyncActions<T> {
  execute: (asyncFunction: () => Promise<T>) => Promise<T>;
  reset: () => void;
  setData: (data: T | null) => void;
  setError: (error: string | null) => void;
}

/**
 * Generic hook for handling async operations with loading and error states.
 *
 * @template T The type of data being loaded
 * @returns State and actions for managing async operations
 *
 * @example
 * const { data, loading, error, execute } = useAsync<User>();
 * const user = await execute(() => fetchUser(id));
 */
export function useAsync<T>(): UseAsyncState<T> & UseAsyncActions<T> {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (asyncFunction: () => Promise<T>): Promise<T> => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await asyncFunction();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err: any) {
      const errorMessage = err?.message || 'An error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState((prev) => ({ ...prev, data }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  return { ...state, execute, reset, setData, setError };
}

/**
 * Hook for managing a list of items with CRUD operations.
 *
 * @template T The type of items in the list
 * @returns List state and actions
 */
export function useList<T extends { id: number | string }>(initialData: T[] = []) {
  const [items, setItems] = useState<T[]>(initialData);

  const add = useCallback((item: T) => {
    setItems((prev) => [...prev, item]);
  }, []);

  const update = useCallback((id: number | string, updates: Partial<T>) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, ...updates } : item
      )
    );
  }, []);

  const remove = useCallback((id: number | string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const replace = useCallback((newItems: T[]) => {
    setItems(newItems);
  }, []);

  const find = useCallback((id: number | string) => {
    return items.find((item) => item.id === id);
  }, [items]);

  return { items, add, update, remove, replace, find };
}

/**
 * Hook for managing form state with validation.
 *
 * @template T The shape of the form data
 * @param initialValues Initial form state
 * @returns Form state and handlers
 */
export function useForm<T extends Record<string, any>>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const setField = useCallback((field: keyof T, value: any) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    // Clear error when field is edited
    setErrors((prev) => ({ ...prev, [field]: '' }));
  }, []);

  const setFieldError = useCallback((field: string, error: string) => {
    setErrors((prev) => ({ ...prev, [field]: error }));
  }, []);

  const setFieldTouched = useCallback((field: string, touched: boolean = true) => {
    setTouched((prev) => ({ ...prev, [field]: touched }));
  }, []);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const setFieldsError = useCallback((fieldErrors: Record<string, string>) => {
    setErrors(fieldErrors);
  }, []);

  return {
    values,
    errors,
    touched,
    setField,
    setFieldError,
    setFieldTouched,
    setFieldsError,
    resetForm,
    setValues,
  };
}

/**
 * Hook for managing a modal dialog state.
 *
 * @template T Optional data to pass to the modal
 * @returns Modal state and handlers
 */
export function useModal<T = null>() {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<T | null>(null);

  const openModal = useCallback((modalData?: T) => {
    setData(modalData || null);
    setOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setOpen(false);
    setData(null);
  }, []);

  return {
    open,
    data,
    openModal,
    closeModal,
  };
}

/**
 * Hook for managing pagination state.
 *
 * @param defaultLimit Default items per page
 * @returns Pagination state and handlers
 */
export function usePagination(defaultLimit = 100) {
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(defaultLimit);
  const [total, setTotal] = useState(0);

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= totalPages) {
      setSkip((page - 1) * limit);
    }
  }, [limit, totalPages]);

  const nextPage = useCallback(() => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1);
    }
  }, [currentPage, totalPages, goToPage]);

  const prevPage = useCallback(() => {
    if (currentPage > 1) {
      goToPage(currentPage - 1);
    }
  }, [currentPage, goToPage]);

  const reset = useCallback(() => {
    setSkip(0);
  }, []);

  return {
    skip,
    limit,
    total,
    currentPage,
    totalPages,
    setLimit,
    setTotal,
    goToPage,
    nextPage,
    prevPage,
    reset,
  };
}

/**
 * Hook for managing debounced search input.
 *
 * @param onSearch Callback when search completes
 * @param delayMs Debounce delay in milliseconds
 * @returns Search state and handlers
 */
export function useDebounceSearch(onSearch: (query: string) => void, delayMs = 300) {
  const [query, setQuery] = useState('');
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      onSearch(query);
    }, delayMs);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query, delayMs, onSearch]);

  return { query, setQuery };
}

/**
 * Hook for managing confirmation dialog state.
 *
 * @returns Confirmation dialog state and handlers
 */
export function useConfirmDialog() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const resolveRef = useRef<(value: boolean) => void>();

  const confirm = useCallback((confirmMessage: string = 'Are you sure?'): Promise<boolean> => {
    return new Promise((resolve) => {
      setMessage(confirmMessage);
      setOpen(true);
      resolveRef.current = resolve;
    });
  }, []);

  const handleConfirm = useCallback(() => {
    resolveRef.current?.(true);
    setOpen(false);
  }, []);

  const handleCancel = useCallback(() => {
    resolveRef.current?.(false);
    setOpen(false);
  }, []);

  return {
    open,
    message,
    confirm,
    handleConfirm,
    handleCancel,
  };
}
