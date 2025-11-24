import { TASK_STATUSES } from '../config/statuses';

export const STATUSES = {
  PROPOSED: 0,
  INPROGRESS: 1,
  BLOCKED: 2,
  DONE: 3,
  NOT_INTERESTED: 4,
  ALREADY_DONE: 5,
};

export const STATUS_TEXT = {
  0: 'Nouveau',
  1: 'En cours',
  2: 'En attente',
  3: 'Faite',
  4: 'Non applicable',
  5: 'Faite', // ALREADY_DONE: Legacy status, kind of
};

export const STATUS_HUMAN_READ = {
  nouveau: 'Nouvelle recommandation',
  'en cours': 'En cours',
  bloquée: 'Bloquée',
  terminée: 'Terminée',
  'pas intéressé': 'Non applicable',
  'déjà faite': 'Déjà faite',
};

export function humanReadableTaskStatus(status) {
  return STATUS_HUMAN_READ[status];
}

export function statusText(status) {
  return STATUS_TEXT[status];
}

export function isStatus(task, status) {
  return task.status === status;
}

export function isArchivedStatus(status) {
  return (
    status === STATUSES.DONE ||
    status === STATUSES.NOT_INTERESTED ||
    status === STATUSES.ALREADY_DONE
  );
}

export function isStatusUpdate(followup) {
  return (
    isArchivedStatus(followup.status) ||
    (followup.comment === '' && followup.contact == null)
  );
}

export function truncate(input, size = 30) {
  if (input.length > size) {
    const truncated = input.substring(0, size);

    // If the truncated string does not contain an opening <a> tag, we can safely truncate it
    if (!truncated.includes('<a')) {
      return `${truncated}...`;
    }

    // If the truncated string contains an opening <a> tag, we need to find the closing </a> tag
    const indexLink = input.indexOf('</a>');
    return `${input.substring(0, indexLink + 4)}...`;
  }
  return input;
}
