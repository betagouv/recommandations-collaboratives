const STATUSES = {
    PROPOSED: 0,
    INPROGRESS: 1,
    BLOCKED: 2,
    DONE: 3,
    NOT_INTERESTED: 4,
    ALREADY_DONE: 5,
}

function taskUrl(projectId, taskId) {
    return `/api/projects/${projectId}/tasks/${taskId}/`
}

function tasksUrl(projectId) {
    return `/api/projects/${projectId}/tasks/`
}

function moveTaskUrl(projectId, taskId) {
    return `/api/projects/${projectId}/tasks/${taskId}/move/`
}

function taskNotificationsUrl(projectId, taskId) {
    return `/api/projects/${projectId}/tasks/${taskId}/notifications/`
}

function markTaskNotificationsAsReadUrl(projectId, taskId) {
    return `/api/projects/${projectId}/tasks/${taskId}/notifications/mark_all_as_read/`
}

function followupsUrl(projectId, taskId) {
    return `/api/projects/${projectId}/tasks/${taskId}/followups/`
}

function followupUrl(projectId, taskId, followupId) {
    return `/api/projects/${projectId}/tasks/${taskId}/followups/${followupId}/`
}

function resourcePreviewUrl(resourceId) {
    return `/ressource/${resourceId}/embed`;
}


// Non API routes
// TODO : Make them into proper endpoints
function editTaskUrl(taskId) {
    return `/task/${taskId}/update/`;
}

function deleteTaskReminderUrl(taskId) {
    return `/task/${taskId}/remind-delete/`;
}

function editReminderUrl(taskId) {
    return `/task/${taskId}/remind/`;
}

// Utilities
function isArchivedStatus(status) {
    return status === STATUSES.DONE
        || status === STATUSES.NOT_INTERESTED
        || status === STATUSES.ALREADY_DONE
}

function isStatusUpdate(followup) {
    return isArchivedStatus(followup.status) || followup.comment === "";
}

const STATUS_TEXT = {
    0: "nouveau",
    1: "en cours",
    2: "en attente",
    3: "faite",
    4: "non applicable",
    5: "faite" // ALREADY_DONE: Legacy status, kind of
}

function statusText(status) {
    return STATUS_TEXT[status];
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString("fr-FR");
}

function renderMarkdown(content) {
    return marked.parse(content);
}

function daysFromNow(days) {
    return new Date((new Date()).getTime() + (days * 86400000 /* seconds in a day */))
}

function formatReminderDate(date) {
    return date.toISOString().substring(0, 10);
}

function reminderTooltip(task) {
    if (task.reminders.length > 0) {
        const reminder = task.reminders[0];
        return `Rappel pour ${reminder.recipient} prévu le ${reminder.deadline}`
    } else {
        return "Aucun rappel prévu"
    }
}

function toArchiveTooltip() {
    return 'Archiver cette action'
}

function generateGravatarUrl(person, size = 50) {
    const hash = md5(person.email);
    let name = `${person.first_name}+${person.last_name}`;
    if (name.trim() === "+") name = "Inconnu";
    const encoded_fallback_uri = encodeURIComponent(`https://ui-avatars.com/api/${name}/${size}`);
    return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`
}
