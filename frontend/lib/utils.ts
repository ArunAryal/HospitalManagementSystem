import { format, parseISO, differenceInYears } from 'date-fns';

export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy');
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateStr?: string | null, timeStr?: string): string {
  if (!dateStr) return '—';
  try {
    const combined = timeStr ? `${dateStr}T${timeStr}` : dateStr;
    return format(parseISO(combined), 'MMM d, yyyy h:mm a');
  } catch {
    return dateStr;
  }
}

export function calcAge(dob?: string | null): string {
  if (!dob) return '—';
  try {
    return `${differenceInYears(new Date(), parseISO(dob))} yrs`;
  } catch {
    return '—';
  }
}

export function formatCurrency(amount?: number | null): string {
  if (amount == null || isNaN(amount)) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'NPR' }).format(amount);
}

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function parseValidationError(errorMsg: string): Record<string, string> {
  const fieldErrors: Record<string, string> = {};
  // Parse error messages like "Field: error message" or extract from API errors
  const parts = errorMsg.split('; ');
  parts.forEach(part => {
    const match = part.match(/^([^:]+):\s*(.+)$/);
    if (match) {
      const [, field, msg] = match;
      fieldErrors[field.toLowerCase().replace(/\s+/g, '_')] = msg.trim();
    }
  });
  return fieldErrors;
}

export const STATUS_COLORS: Record<string, string> = {
  Scheduled: 'bg-blue-50 text-blue-700 ring-blue-200',
  Completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  Cancelled: 'bg-red-50 text-red-700 ring-red-200',
  'No-Show': 'bg-amber-50 text-amber-700 ring-amber-200',
  Active: 'bg-blue-50 text-blue-700 ring-blue-200',
  Discharged: 'bg-slate-50 text-slate-600 ring-slate-200',
  Pending: 'bg-amber-50 text-amber-700 ring-amber-200',
  Paid: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  'Partially Paid': 'bg-orange-50 text-orange-700 ring-orange-200',
  Partial: 'bg-orange-50 text-orange-700 ring-orange-200',
  Available: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  'Partially Occupied': 'bg-blue-50 text-blue-700 ring-blue-200',
  'Fully Occupied': 'bg-red-50 text-red-700 ring-red-200',
  Occupied: 'bg-red-50 text-red-700 ring-red-200',
  Maintenance: 'bg-amber-50 text-amber-700 ring-amber-200',
};
