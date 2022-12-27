import Alpine from 'alpinejs'

import api, { tasksUrl, taskUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

export const STATUSES = {
    PROPOSED: 0,
    INPROGRESS: 1,
    BLOCKED: 2,
    DONE: 3,
    NOT_INTERESTED: 4,
    ALREADY_DONE: 5,
}

Alpine.store('tasks', {
    tasks: [],
    boards: [],
    async getTasks(projectId) {
        const json = await api.get(tasksUrl(projectId))

        const data = json.data.map(d => Object.assign(d, {
            uuid: generateUUID()
        }));

        return this.tasks = data;
    },
    async patchTask(taskId, patch) {
        await api.patch(taskUrl(this.projectId, taskId), patch)
    },
    getBoards() {
        return this.boards = [
            { status: STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary", color: "#0d6efd" },
            { status: STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary", color: "#6c757d" },
            { status: STATUSES.BLOCKED, title: "En attente", color_class: "border-warning", color: "#ffc107" },
            { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color: "#adb5bd" },
        ]
    }
})

export default Alpine.store('tasks')
