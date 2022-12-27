import Alpine from "alpinejs"
import { STATUSES } from '../store/tasks'

import api, { taskUrl, editTaskUrl, deleteTaskReminderUrl, followupUrl, followupsUrl, moveTaskUrl, markTaskNotificationsAsReadUrl, taskNotificationsUrl } from '../utils/api'
import { formatReminderDate, daysFromNow, formatDate } from '../utils/date'
import { isStatusUpdate, statusText } from "../utils/taskStatus"
import { toArchiveTooltip, reminderTooltip } from '../utils/tooltip'
import { renderMarkdown } from '../utils/markdown'
import { generateGravatarUrl } from '../utils/gravatar'

Alpine.data("KanbanTasks", boardTasksApp)

function boardTasksApp(projectId) {

    const moveTask = async (taskId, otherTaskId, below) => {
        const params = new URLSearchParams(`${below ? 'below' : 'above'}=${otherTaskId}`);
        await api.post(moveTaskUrl(projectId, taskId), params, {
            headers: { 'content-type': 'application/x-www-form-urlencoded' },
        })
    }

    const issueFollowup = async (task, status, comment = "") => {
        const body = { comment, status }

        if (body.status === task.status && body.comment === "") return;

        await api.post(followupsUrl(projectId, task.id), body)
    }

    const editComment = async (taskId, followupId, comment) => {
        await api.patch(followupUrl(projectId, taskId, followupId), { comment })
    }

    const patchTask = async (taskId, patch) => {
        await api.patch(taskUrl(projectId, taskId), patch)
    }

    const markAllAsRead = async (taskId) => {
        await api.post(markTaskNotificationsAsReadUrl(projectId, taskId), {})
    }

    const app = {
        init() {
            console.log('lol');
        },
        //utils function
        renderMarkdown,
        formatDate,
        isStatusUpdate,
        statusText,
        generateGravatarUrl,
        toArchiveTooltip,
        reminderTooltip,
        editTaskUrl,
        deleteTaskReminderUrl,
        //Event listener dispatched by another component
        async handleIssueFollowup(e) {
            await issueFollowup(e.detail.task, e.detail.status)
            await this.getData()
        },
        data: [],
        boards: [],
        STATUSES: STATUSES,
        get isBusy() {
            return this.$store.app.isLoading
        },
        currentlyHoveredElement: null,
        async getData() {
            return this.data = await this.$store.tasks.getTasks(projectId)
        },
        async getBoards() {
            return this.boards = await this.$store.tasks.getBoards()
        },
        getStatuses() {
            console.log('lol');
            console.log(this.$store.tasks.STATUSES)
            return this.STATUSES = this.$store.tasks.STATUSES
        },
        sortFn(a, b) {
            return a.order - b.order;
        },
        filterFn(d) {
            return this.canAdministrate || d.public;
        },
        findByUuid(uuid) {
            return this.data.find(d => d.uuid === uuid);
        },
        findById(id) {
            return this.data.find(d => d.id === id);
        },
        get view() {
            const result = this.data.filter((d) => this.filterFn(d)).sort((a, b) => this.sortFn(a, b));
            return result;
        },
        column(status) {
            if (status instanceof Array) {
                return this.view.filter(d => status.indexOf(d.status) !== -1);
            } else {
                return this.view.filter(d => d.status === status);
            }
        },
        onDragStart(event, uuid) {
            event.dataTransfer.clearData();
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData('application/uuid', uuid);
            event.target.classList.add('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.add("drop-highlight"));
        },
        onDragEnd(event) {
            event.target.classList.remove('drag-dragging');
            document.querySelectorAll(".drop-column").forEach(e => e.classList.remove("drop-highlight"));
        },
        onDragEnter(event) {
            if (this.currentlyHoveredElement && this.currentlyHoveredElement !== event.currentTarget) {
                this.currentlyHoveredElement.classList.remove('drag-target');
            }
            this.currentlyHoveredElement = event.currentTarget;
            event.currentTarget.classList.add('drag-target');
        },
        onDragLeave(event) {
            if (event.target === this.currentlyHoveredElement) {
                event.target.classList.remove('drag-target');
            }
        },
        onDragOver(event) {
            event.preventDefault();
            event.dataTransfer.dropEffect = "move";
        },
        async onDrop(event, status, targetUuid) {
            event.preventDefault();

            this.currentlyHoveredElement.classList.remove('drag-target');
            this.currentlyHoveredElement = null;

            const uuid = event.dataTransfer.getData("application/uuid");

            const data = this.data.find(d => d.uuid === uuid);
            const nextData = this.data.find(d => d.uuid === targetUuid);

            if (status instanceof Array) {
                if (isArchivedStatus(data.status) && nextData) {
                    await moveTask(data.id, nextData.id);
                } else {
                    this.openFeedbackModal(data);
                }
            } else {
                await issueFollowup(data, status);
                if (nextData) await moveTask(data.id, nextData.id);
            }

            await this.getData();
        },
        // Boards
        // boards: [
        //     { status: STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary" },
        //     { status: STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary" },
        //     { status: STATUSES.BLOCKED, title: "En attente", color_class: "border-warning" },
        //     { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error" },
        // ],

        // Administrate
        canAdministrate: false,
        loadCanAdministrate() {
            const canAdministrate = document.getElementById("canAdministrate").textContent;
            this.canAdministrate = JSON.parse(canAdministrate);
        },

        canManage: false,
        loadCanManage() {
            const canManage = document.getElementById("canManage").textContent;
            this.canManage = JSON.parse(canManage);
        },

        isSwitchtender: false,
        loadIsSwitchtender() {
            const isSwitchtender = document.getElementById("isSwitchtender").textContent;
            this.isSwitchtender = JSON.parse(isSwitchtender);
        },

        // UserId
        userEmail: null,
        loadUserId() {
            const userEmail = document.getElementById("userEmail").textContent;
            this.userEmail = JSON.parse(userEmail);
        },

        // Tooltips
        initTooltips() {
            new bootstrap.Tooltip(this.$el, {
                selector: "[data-bs-toggle='tooltip']"
            })
        },

        // URL Parsing trickery
        processUrl() {
            const match = location.hash.match(/^#action-(\d+)/);
            if (match) {
                this.currentTaskId = parseInt(match[1], 10);
            }
        },

        // Previews
        currentTaskId: null,
        currentTaskFollowups: null,
        currentTaskNotifications: [],
        async loadFollowups(taskId) {
            const { data } = await api.get(followupsUrl(projectId, taskId));
            this.currentTaskFollowups = data
        },
        async loadNotifications(taskId) {
            const { data } = await api.get(taskNotificationsUrl(projectId, taskId));
            this.currentTaskNotifications = data;
        },
        initPreviewModal() {

            const element = document.getElementById("task-preview");
            this.previewModalHandle = new bootstrap.Modal(element);

            const cleanup = () => {
                // FIXME : Race condition when bootstrap unloads modal
                // this.currentTaskId = null;
                // this.currentTaskFollowups = null;
                // this.currentTaskNotifications = [];

                //Cleaning status changes behaviour
                this.$refs.commentTextRef.classList.remove('textarea-highlight');
                this.$refs.commentTextFormRef.classList.remove('tooltip-highlight');
                this.$refs.commentTextRef.placeholder = "Votre message";

                this.pendingComment = "";
                this.currentlyEditing = null;
                location.hash = '';
            }


            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener('hidden.bs.modal', cleanup);
            if (this.currentTaskId) this.openPreviewModal();
            window.addEventListener('hashchange', event => {
                if (location.hash === '') {
                    this.previewModalHandle.hide();
                }
            });
        },
        async onPreviewClick(id) {
            this.currentTaskId = id;
            this.openPreviewModal();
        },
        async openPreviewModal() {
            location.hash = `#action-${this.currentTaskId}`;
            this.previewModalHandle.show();

            this.loadFollowups(this.currentTaskId);
            this.loadNotifications(this.currentTaskId);

            if (!this.canAdministrate) {
                await patchTask(this.currentTaskId, { visited: true });
            }

            await markAllAsRead(this.currentTaskId);
            await this.getData();
        },
        async onSetTaskPublic(id, value) {
            await patchTask(id, { public: value });
            await this.getData();
        },
        hasNotification(followupId) {
            return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
        },

        // Comments
        pendingComment: "",
        currentlyEditing: null,
        onEditComment(followup) {
            this.pendingComment = followup.comment;
            this.currentlyEditing = ["followup", followup.id];
            this.$refs.commentTextRef.focus();
        },
        onEditContent() {
            this.pendingComment = this.currentTask.content;
            this.currentlyEditing = ["content", this.currentTask.id];
            this.$refs.commentTextRef.focus();
        },
        async onSubmitComment() {
            if (!this.currentlyEditing) {
                await issueFollowup(this.currentTask, undefined, this.pendingComment);
                await this.getData()
                await this.loadFollowups(this.currentTask.id);
            } else {
                const [type, id] = this.currentlyEditing;
                if (type === "followup") {
                    await editComment(this.currentTask.id, id, this.pendingComment);
                    await this.loadFollowups(this.currentTask.id);
                } else if (type === "content") {
                    await patchTask(this.currentTask.id, { content: this.pendingComment });
                    await this.getData();
                }
            }
            this.pendingComment = "";
            this.currentlyEditing = null;
        },

        // Reminiders
        currentReminderTaskId: null,
        pendingReminderDate: formatReminderDate(daysFromNow(30 * 6)),
        initReminderModal() {
            const element = document.getElementById("reminder-modal");
            this.reminderModalHandle = new bootstrap.Modal(element);
            const cleanup = () => {
                this.currentReminderTaskId = null;
                this.pendingReminderDate = formatReminderDate(daysFromNow(30 * 6));
            };
            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener("hidden.bs.modal", cleanup);
        },
        onReminderClick(id) {
            const task = this.findById(id)
            if (task.reminders.length > 0)
                this.pendingReminderDate = task.reminders[0].deadline
            this.currentReminderTaskId = task.id;
            this.openReminderModal();
        },
        openReminderModal() {
            this.reminderModalHandle.show();
        },
        onSubmitReminder() {
            const form = this.$refs.reminderForm;
            const dateInput = form.querySelector('#reminder-date');
            const daysInput = form.querySelector('#reminder-days');
            daysInput.value = Math.ceil((new Date(dateInput.value) - new Date()) / 86400000);
            form.submit();
        },
        updatePendingReminderDate(days) {
            this.pendingReminderDate = formatReminderDate(daysFromNow(days));
        },

        // Feedback
        feedbackStatus: STATUSES.DONE,
        feedbackComment: '',
        feedbackModal: null,
        currentFeedbackTask: null,
        initFeedbackModal() {
            const element = document.getElementById("feedback-modal");
            this.feedbackModal = new bootstrap.Modal(element);
            const cleanup = () => {
                this.feedbackStatus = 3;
                this.feedbackComment = '';
                this.currentFeedbackTask = null;
            }
            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener("hidden.bs.modal", cleanup);
        },
        openFeedbackModal(task) {
            this.currentFeedbackTask = task;
            this.feedbackModal.show();
        },
        async onSubmitFeedback() {
            await issueFollowup(this.currentFeedbackTask, this.feedbackStatus, this.feedbackComment)
            await this.getData();
            this.feedbackStatus = 3;
            this.feedbackComment = '';
            this.currentFeedbackTask = null;
            this.feedbackModal.hide();
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
        truncate(input, size = 30) {
            return input.length > size ? `${input.substring(0, size)}...` : input;
        },
        formatDateDisplay(date) {
            return new Date(date).toLocaleDateString('fr-FR');
        }
    };

    return app
}
