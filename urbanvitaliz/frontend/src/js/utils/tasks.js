export const STATUSES = {
    PROPOSED: 0,
    INPROGRESS: 1,
    BLOCKED: 2,
    DONE: 3,
    NOT_INTERESTED: 4,
    ALREADY_DONE: 5,
}

// Utilities
export function isArchivedStatus(status) {
    return status === STATUSES.DONE
        || status === STATUSES.NOT_INTERESTED
        || status === STATUSES.ALREADY_DONE
}

export function isStatusUpdate(followup) {
    return isArchivedStatus(followup.status) || followup.comment === "";
}

const STATUS_TEXT = {
    0: "nouveau",
    1: "En cours",
    2: "en attente",
    3: "Fait",
    4: "Non applicable",
    5: "faite" // ALREADY_DONE: Legacy status, kind of
}

export function statusText(status) {
    return STATUS_TEXT[status];
}

export function isStatus(task, status) {
    return task.status === status
}
 