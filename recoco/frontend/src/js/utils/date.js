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
