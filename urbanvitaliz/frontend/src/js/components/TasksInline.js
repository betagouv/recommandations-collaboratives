import Alpine from 'alpinejs'
import TaskApp from './Tasks'
import { STATUSES } from '../config/statuses';

function TasksInline(projectId) {

    const app = {
        currentStatus: 'all',
        boardsFiltered: [],
        // boards: [
        //     { status: [STATUSES.PROPOSED, STATUSES.INPROGRESS, STATUSES.BLOCKED], title: "Archivées", color_class: "border-error", color: "#0d6efd" },
        //     { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color: "#adb5bd" },
        // ],
        boards: [
            { status: STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary", color: "#0d6efd" },
            { status: STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary", color: "#6c757d" },
            { status: STATUSES.BLOCKED, title: "En attente", color_class: "border-warning", color: "#ffc107" },
            { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color: "#adb5bd" },
        ],
        init() {
            this.boardsFiltered = this.boards
        },
        handleStatusFilterClick(status) {

            if (this.currentStatus === status || status === 'all') {
                this.currentStatus = 'all'
                return this.boardsFiltered = this.boards
            }


            this.currentStatus = status

            return this.boardsFiltered = this.boards.filter(board => board.status === status);
        }
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
