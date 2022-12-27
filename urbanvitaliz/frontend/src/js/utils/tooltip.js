export function reminderTooltip(task) {
    if (task.reminders.length > 0) {
        const reminder = task.reminders[0];
        return `Rappel pour ${reminder.recipient} prévu le ${reminder.deadline}`
    } else {
        return "Aucun rappel prévu"
    }
}

export function toArchiveTooltip() {
    return 'Archiver cette action'
}
