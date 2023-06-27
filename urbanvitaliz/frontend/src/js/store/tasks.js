import Alpine from 'alpinejs'
import api, { tasksUrl, moveTaskUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

Alpine.store('tasksView', {
    currentView: 'inline',
    init() {
        console.log('tasks view store init ');
    },
    switchView() {
        this.currentView === 'inline' ? this.currentView = 'kanban' : this.currentView = 'inline'
    },
})

Alpine.store('tasksData', {
    tasks: [],
    init() {
        console.log('tasks data store init ');
    },
    async getTasks(projectId) {
        const json = await api.get(tasksUrl(projectId))

        const data = json.data.map(d => Object.assign(d, {
            uuid: generateUUID()
        }));

        return this.tasks = data;
    },
    async moveTask(taskId, otherTaskId, below) {
        const params = new URLSearchParams(`${below ? 'below' : 'above'}=${otherTaskId}`);
        await api.post(moveTaskUrl(projectId, taskId), params, {
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
        })
    },
    // Movement Buttons
    async moveAbove(task, otherTask) {
        await moveTask(task.id, otherTask.id);
        await this.getData();
    },
    async moveBelow(task, otherTask) {
        await moveTask(task.id, otherTask.id, true);
        await this.getData();
    },
    async patchTask(taskId, patch) {
        await api.patch(taskUrl(projectId, taskId), patch)
    },
    async editComment(taskId, followupId, comment) {
        await api.patch(followupUrl(projectId, taskId, followupId), { comment })
    },
    async markAllAsRead(taskId) {
        await api.post(markTaskNotificationsAsReadUrl(projectId, taskId), {})
    },
    async issueFollowup(task, status, comment = "") {
        const body = { comment, status }

        if (body.status === task.status && body.comment === "") return;

        await api.post(followupsUrl(projectId, task.id), body)
    },
    async loadFollowups(taskId) {
        const { data } = await api.get(followupsUrl(projectId, taskId));
        this.currentTaskFollowups = data
    },
    async loadNotifications(taskId) {
        const { data } = await api.get(taskNotificationsUrl(projectId, taskId));
        this.currentTaskNotifications = data;
    },
})

Alpine.store('tasksUi', {
    init() {
        console.log('tasksUi store init ');
    },
    findByUuid(uuid) {
        return this.tasks.find(d => d.uuid === uuid);
    },
    findById(id) {
        return this.tasks.find(d => d.id === id);
    },
})

Alpine.store('currentTask', {
    init() {
        console.log('current task store init ');
    },
})



export default Alpine.store('tasks')
