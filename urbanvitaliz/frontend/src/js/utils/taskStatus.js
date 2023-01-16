import { STATUSES } from '../config/statuses';

export const STATUS_TEXT = {
    0: "nouveau",
    1: "en cours",
    2: "en attente",
    3: "faite",
    4: "non applicable",
    5: "faite" // ALREADY_DONE: Legacy status, kind of
}

export function statusText(status) {
    return STATUS_TEXT[status];
}

export function isArchivedStatus(status) {
    return status === STATUSES.DONE
        || status === STATUSES.NOT_INTERESTED
        || status === STATUSES.ALREADY_DONE
}

export function isStatusUpdate(followup) {
    return isArchivedStatus(followup.status) || followup.comment === "";
}
