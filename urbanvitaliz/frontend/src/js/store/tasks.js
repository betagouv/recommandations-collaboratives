import Alpine from 'alpinejs'

import api, { tasksUrl,taskUrl, followupUrl, followupsUrl, moveTaskUrl, markTaskNotificationsAsReadUrl, taskNotificationsUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'
import { renderMarkdown } from '../utils/markdown';

Alpine.store('tasks', {
    data: [],
    setProjectId(projectId) {
        this.projectId = projectId
        console.log('project id ?', this.projectId);
    },
    async getData(projectId) {

        if (!projectId) projectId = this.projectId

        console.log('store : tasks : get data')
        const json = await api.get(tasksUrl(projectId))

        const data = json.data.map(d => Object.assign(d, {
            uuid: generateUUID()
        }));

        this.data = data;

        console.log('project tasks : ', this.data);
    },
    filterByStatusAndOrder(status) {
        let dataFiltered = []

        if (status instanceof Array) {
            dataFiltered = this.data.filter(task => status.indexOf(task.status) !== -1);
        } else {
            dataFiltered = this.data.filter(task => task.status === status)
        }

        return dataFiltered.sort((a, b) => a.order - b.order)
    },
    renderMarkdown(content) {
        return renderMarkdown(content)
    },
    //Previews
    currentTask: null,
    currentTaskId: null,
    currentTaskFollowups: null,
    currentTaskNotifications: [],
    getCurrentTask(taskId) {
        this.currentTask = this.findById(taskId)

        console.log('current task ? ', this.currentTask);
    },
    initPreviewModal() {

        console.log('init preview modal from store ? ');

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
            await this.patchTask(this.currentTaskId, { visited: true });
        }

        await this.markAllAsRead(this.currentTaskId);
        await this.getData();
    },
    async loadFollowups(taskId) {
        const { data } = await api.get(followupsUrl(this.projectId, taskId));
        this.currentTaskFollowups = data
    },
    async loadNotifications(taskId) {
        const { data } = await api.get(taskNotificationsUrl(this.projectId, taskId));
        this.currentTaskNotifications = data;
    },
    findById(id) {
        return this.data.find(d => d.id === id);
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
    async issueFollowup(task, status, comment = "") {
        const body = { comment, status }

        if (body.status === task.status && body.comment === "") return;

        await api.post(followupsUrl(this.projectId, task.id), body)
    },
    async editComment(taskId, followupId, comment) {
        await api.patch(followupUrl(this.projectId, taskId, followupId), { comment })
    },
    async onSubmitComment() {
        if (!this.currentlyEditing) {
            // await this.issueFollowup(this.currentTask, undefined, this.pendingComment);
            console.log(this.projectId)
            console.log(this.currentTask)
            await api.post(followupsUrl(this.projectId, this.currentTask.id), {comment:this.pendingComment, status:undefined})
            await this.getData()
            await this.loadFollowups(this.currentTask.id);
        } else {
            const [type, id] = this.currentlyEditing;
            if (type === "followup") {
                await this.editComment(this.currentTask.id, id, this.pendingComment);
                await this.loadFollowups(this.currentTask.id);
            } else if (type === "content") {
                await this.patchTask(this.currentTask.id, { content: this.pendingComment });
                await this.getData();
            }
        }
        this.pendingComment = "";
        this.currentlyEditing = null;
    },
    async markAllAsRead(taskId) {
        console.log(this.projectId);
        await api.post(markTaskNotificationsAsReadUrl(this.projectId, taskId), {})
    },
    hasNotification(followupId) {
        return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
    },
    isStatusUpdate(followup) {
        return this.isArchivedStatus(followup.status) || followup.comment === "";
    },
    formatDate(timestamp) {
        return new Date(timestamp).toLocaleDateString("fr-FR");
    },
    isArchivedStatus(status) {
        console.log('store board ?', this.$store.boards.STATUSES);
        return status === this.$store.boards.STATUSES.DONE
            || status === this.$store.boards.STATUSES.NOT_INTERESTED
            || status === this.$store.boards.STATUSES.ALREADY_DONE
    },
    async patchTask(taskId, patch) {
        await api.patch(taskUrl(this.projectId, taskId), patch)
    },
    moveAbove() {

    },
    moveBelow() {

    }

})

export default Alpine.store('tasks')
