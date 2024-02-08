export function reminderTooltip(task) {

    if (task.reminders.length > 0) {
        const reminder = task.reminders[0];

        if (isOldReminder(reminder)) return "Aucun rappel prévu"

        return `Rappel pour ${reminder.recipient} prévu le ${reminder.deadline}`
    } else {
        return "Aucun rappel prévu"
    }
}

export function isOldReminder(reminder) {
    if (!reminder) return false

    const now = new Date().getTime();
    const reminderDate = new Date(reminder.deadline).getTime();

    return (reminderDate < now)
}

export function toArchiveTooltip() {
    return 'Archiver cette action'
}
