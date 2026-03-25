'use client';

/**
 * Custom hooks for form validation.
 *
 * These hooks provide reusable validation logic for common field types
 * and patterns used throughout the application.
 */

import { useCallback } from 'react';

export type ValidationRule = {
  validate: (value: any) => boolean;
  message: string;
};

/**
 * Hook for field-level validation.
 *
 * @param rules Array of validation rules
 * @returns Validation function and error message
 */
export function useFieldValidation(rules: ValidationRule[]) {
  const validate = useCallback((value: any): string | null => {
    for (const rule of rules) {
      if (!rule.validate(value)) {
        return rule.message;
      }
    }
    return null;
  }, [rules]);

  return { validate };
}

/**
 * Common validation rules.
 */
export const ValidationRules = {
  required: (message = 'This field is required'): ValidationRule => ({
    validate: (v) => v !== null && v !== undefined && v !== '',
    message,
  }),

  email: (message = 'Invalid email address'): ValidationRule => ({
    validate: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
    message,
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    validate: (v) => v?.length >= min,
    message: message || `Must be at least ${min} characters`,
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    validate: (v) => v?.length <= max,
    message: message || `Must be no more than ${max} characters`,
  }),

  pattern: (regex: RegExp, message = 'Invalid format'): ValidationRule => ({
    validate: (v) => regex.test(v),
    message,
  }),

  phone: (message = 'Invalid phone number'): ValidationRule => ({
    validate: (v) => {
      const digits = (v || '').replace(/\D/g, '');
      return digits.length >= 10 && digits.length <= 15;
    },
    message,
  }),

  number: (message = 'Must be a number'): ValidationRule => ({
    validate: (v) => !isNaN(v) && v !== '',
    message,
  }),

  positiveNumber: (message = 'Must be a positive number'): ValidationRule => ({
    validate: (v) => !isNaN(v) && parseFloat(v) > 0,
    message,
  }),

  minValue: (min: number, message?: string): ValidationRule => ({
    validate: (v) => parseFloat(v) >= min,
    message: message || `Must be at least ${min}`,
  }),

  maxValue: (max: number, message?: string): ValidationRule => ({
    validate: (v) => parseFloat(v) <= max,
    message: message || `Must be no more than ${max}`,
  }),

  date: (message = 'Invalid date'): ValidationRule => ({
    validate: (v) => !isNaN(new Date(v).getTime()),
    message,
  }),

  futureDate: (message = 'Date must be in the future'): ValidationRule => ({
    validate: (v) => {
      const inputDate = new Date(v);
      const today = new Date();
      // Compare only the date part (set time to 00:00 for both)
      inputDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      return inputDate > today;
    },
    message,
  }),

  pastDate: (message = 'Date must be in the past'): ValidationRule => ({
    validate: (v) => {
      const inputDate = new Date(v);
      const today = new Date();
      // Compare only the date part (set time to 00:00 for both)
      inputDate.setHours(0, 0, 0, 0);
      today.setHours(0, 0, 0, 0);
      return inputDate < today;
    },
    message,
  }),

  match: (otherValue: any, message = 'Fields do not match'): ValidationRule => ({
    validate: (v) => v === otherValue,
    message,
  }),
};

/**
 * Hook for validating entire form.
 *
 * @param validationSchema Schema mapping field names to validation rules
 * @returns Validation function
 */
export function useFormValidation(
  validationSchema: Record<string, ValidationRule[]>
) {
  const validateForm = useCallback(
    (values: Record<string, any>): Record<string, string> => {
      const errors: Record<string, string> = {};

      for (const [field, rules] of Object.entries(validationSchema)) {
        const value = values[field];
        for (const rule of rules) {
          if (!rule.validate(value)) {
            errors[field] = rule.message;
            break; // Only show first error per field
          }
        }
      }

      return errors;
    },
    [validationSchema]
  );

  return { validateForm };
}

/**
 * Hook for field-specific validation with debouncing.
 *
 * @param validationSchema Schema mapping field names to validation rules
 * @param delayMs Debounce delay in milliseconds
 * @returns Validation function
 */
export function useDebouncedValidation(
  validationSchema: Record<string, ValidationRule[]>,
  delayMs = 300
) {
  const timeoutsRef: Record<string, NodeJS.Timeout> = {};

  const validateField = useCallback(
    (
      field: string,
      value: any,
      onError: (error: string | null) => void
    ) => {
      // Clear any pending timeout for this field
      if (timeoutsRef[field]) {
        clearTimeout(timeoutsRef[field]);
      }

      // Set a new timeout
      timeoutsRef[field] = setTimeout(() => {
        const rules = validationSchema[field] || [];
        for (const rule of rules) {
          if (!rule.validate(value)) {
            onError(rule.message);
            return;
          }
        }
        onError(null);
      }, delayMs);
    },
    [validationSchema, delayMs]
  );

  return { validateField };
}
