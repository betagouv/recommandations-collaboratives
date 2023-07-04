import Alpine from 'alpinejs'
import api, { tasksUrl, taskUrl, moveTaskUrl, followupsUrl, taskNotificationsUrl, markTaskNotificationsAsReadUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

document.addEventListener('alpine:init', () => {

    Alpine.store('tasksView', {
        currentView: 'kanban',
        init() {
            console.log('tasks view store init ');
        },
        switchView() {
            this.currentView === 'inline' ? this.currentView = 'kanban' : this.currentView = 'inline'
        },
    })

    Alpine.store('tasksData', {
        get projectId() {
            return Alpine.store('djangoData').projectId
        },

        tasks: [],

        // TODO: Extraits plus tard dans djangoData.user
        canUseTasks: false,
        canManageTasks: false,


        async init() {
            await this.loadTasks()
        },

        get newTasks() {
            return this.tasks.filter(task => task.status === 0)
        },

        async loadTasks() {
            const json = await api.get(tasksUrl(this.projectId))

            const data = json.data.map(d => Object.assign(d, {
                // TODO: Virer les UUID
                uuid: generateUUID()
            }));

            this.tasks = data;
        },

        async moveTask(taskId, otherTaskId, below) {
            const params = new URLSearchParams(`${below ? 'below' : 'above'}=${otherTaskId}`);
            await api.post(moveTaskUrl(this.projectId, taskId), params, {
                headers: { 'content-type': 'application/x-www-form-urlencoded' },
            })
            await this.loadTasks();
        },
        // Movement Buttons
        async moveAbove(task, otherTask) {
            await this.moveTask(task.id, otherTask.id);
        },
        async moveBelow(task, otherTask) {
            await this.moveTask(task.id, otherTask.id, true);
        },
        async patchTask(taskId, patch) {
            await api.patch(taskUrl(this.projectId, taskId), patch)
            await this.loadTasks();
        },

        // TODO : Plus tard
        async loadFollowups(taskId) {
            const { data } = await api.get(followupsUrl(this.projectId, taskId));
            console.log('data qsdjklqsdjkljklqsdljk ', data);
            return data
        },
        async loadNotifications(taskId) {
            const { data } = await api.get(taskNotificationsUrl(this.projectId, taskId));
            return data;
        },
        async issueFollowup(task, status, comment = "") {
            const body = { comment, status }

            if (body.status === task.status && body.comment === "") return;

            await api.post(followupsUrl(this.projectId, task.id), body)
        },
        async editComment(taskId, followupId, comment) {
            await api.patch(followupUrl(this.projectId, taskId, followupId), { comment })
        },
        async markAllAsRead(taskId) {
            await api.post(markTaskNotificationsAsReadUrl(this.projectId, taskId), {})
        }
    })

    Alpine.store('previewModal', {
        handle: null,
        task: null,
        followups: null,

        get projectId() {
            return Alpine.store('djangoData').projectId
        },

        init() {
            const element = document.getElementById("test-modal");
            this.handle = new bootstrap.Modal(element);
        },

        open(task) {
            this.task = task
            this.handle.show()
            this.loadFollowups()
        },

        async loadFollowups() {
            const { data } = await api.get(followupsUrl(this.projectId, this.task.id));
            this.followups = data
        },

        close() {
            this.handle.hide()
        },

        cleanup() {
            this.task = null
        },
    })

    Alpine.store('taskModal', {
        currentTask: null,

        previewModalHandle: null,
        deleteModalHandle: null,
        feedbackModalHandle: null,

        onPreviewClick(task) {
            this.currentTask = task
            console.log('preview click ? ', this.currentTask);
            this.previewModalHandle.show();
        },
        onDeleteClick(task) {
            this.currentTask = task
            console.log('delete task ', this.currentTask);
            this.deleteModalHandle.show();
        },
        onFeedbackClick(task) {
            this.currentTask = task
            console.log('delete task ', this.currentTask);
            this.feedbackModalHandle.show();
        }
    })
})

export default Alpine.store('tasks')
