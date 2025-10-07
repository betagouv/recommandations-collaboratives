export function formatDate(
  timestamp,
  options = { year: 'numeric', month: 'numeric', day: 'numeric' }
) {
  return new Date(timestamp).toLocaleDateString('fr-FR', options);
}

export function formatReminderDate(date) {
  return date.toISOString().substring(0, 10);
}

export function daysFromNow(days) {
  return new Date(
    new Date().getTime() + days * 86400000 /* seconds in a day */
  );
}

/**
 * Format date for display in French locale
 */
export function formatDateFrench(dateString, options = {}) {
  if (!dateString) return '';

  const date = new Date(dateString);
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  };

  return date.toLocaleDateString('fr-FR', { ...defaultOptions, ...options });
}
