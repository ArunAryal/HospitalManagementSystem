/**
 * Hooks module - custom React hooks for data fetching, forms, and state management.
 */

export { useAsync, useList, useForm, useModal, usePagination, useDebounceSearch, useConfirmDialog } from './useAsync';
export type { UseAsyncState, UseAsyncActions } from './useAsync';

export { usePatient, usePatients, useDoctor, useDoctors, useAppointment, useAppointments, useMutation, useOptimisticUpdate } from './useData';

export { useFieldValidation, useFormValidation, useDebouncedValidation, ValidationRules } from './useValidation';
export type { ValidationRule } from './useValidation';
