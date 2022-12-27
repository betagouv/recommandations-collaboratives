import Alpine from 'alpinejs'
import TaskApp from './Tasks'
import { STATUSES } from '../config/statuses';

function TasksInline(projectId) {

    const app = {
        boards: [
            { status: STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary", color: "#0d6efd" },
            { status: STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary", color: "#6c757d" },
            { status: STATUSES.BLOCKED, title: "En attente", color_class: "border-warning", color: "#ffc107" },
            { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color: "#adb5bd" },
        ]
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
