import Alpine from 'alpinejs'
import { TASK_STATUSES } from '../config/statuses';

import { renderMarkdown } from '../utils/markdown'
import { formatDate } from '../utils/date'
import { resourcePreviewUrl, deleteTaskUrl } from '../utils/api'
import { gravatar_url } from '../utils/gravatar'
import { isStatusUpdate, statusText, isArchivedStatus } from "../utils/taskStatus"

export default function TaskModal() {
    return {
        currentlyEditing: null,
        pendingComment: '',
        renderMarkdown,
        formatDate,
        resourcePreviewUrl,
        gravatar_url,
        currentTaskFollowups: [],
        currentTaskNotifications: [],
        isStatusUpdate,
        statusText,
        deleteTaskUrl,
        currentDeletingTask: {},
        currentFeedbackTask: {},
        feedbackComment:'',
        feedbackStatus: TASK_STATUSES.DONE,
        init() {
            console.log('task modal initialized');
            // console.log('current task clicked :', this.$store.taskModal.currentTask);
            this.initPreviewModal();
            this.initDeleteTaskConfirmationModal();
            this.initFeedbackModal();
        },
        initPreviewModal() {

            console.log('store task modal ? :', this.$store.taskModal)
            const element = document.getElementById("task-preview");
            this.$store.taskModal.previewModalHandle = new bootstrap.Modal(element);
            // this.store.taskModal.previewModalHandle = new bootstrap.Modal(element);

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
            if (this.$store.taskModal.currentTaskId) this.openPreviewModal();

            window.addEventListener('hashchange', event => {
                if (location.hash === '') {
                    this.$store.taskModal.previewModalHandle.hide();
                }
            });
        },
        async openPreviewModal(e) {

            const task = e.detail
            console.log('dispatched open preview task : ', task);
            console.log('modal com : open preview modal')
            this.$store.taskModal.onPreviewClick(task)
            location.hash = `#action-${task.id}`;

            this.currentTaskFollowups = await this.$store.task.loadFollowups(task.id);
            this.currentTaskNotifications = await this.$store.task.loadNotifications(task.id);

            if (isMember && !isHijacked) await this.$store.taskData.patchTask(task.id, { visited: true });

            await this.$store.task.markAllAsRead(task.id);

            this.followupScrollToLastMessage();

            // await this.getData();
        },
        async onSubmitComment() {
            if (!this.currentlyEditing) {
                await this.$store.task.issueFollowup(this.$store.taskModal.currentTask, undefined, this.pendingComment);
                // await this.getData()
                this.currentTaskFollowups = await this.$store.task.loadFollowups(this.$store.taskModal.currentTask.id);
            } else {
                const [type, id] = this.currentlyEditing;
                if (type === "followup") {
                    await editComment(this.currentTask.id, id, this.pendingComment);
                    await this.loadFollowups(this.currentTask.id);
                } else if (type === "content") {
                    await this.$store.tasksData.patchTask(this.$store.taskModal.currentTask.id, { content: this.pendingComment });
                    await this.getData();
                }
            }

            this.pendingComment = "";
            this.currentlyEditing = null;
            this.followupScrollToLastMessage();
        },
        hasNotification(followupId) {
            return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
        },
        //Event listener dispatched by another component
        async handleIssueFollowup(e) {
            await this.$store.task.issueFollowup(e.detail.task, e.detail.status)
            // await this.getData()
        },
        followupScrollToLastMessage() {
            const scrollContainer = document.getElementById("followups-scroll-container");
            if (scrollContainer) {
                setTimeout(() => {
                    scrollContainer.scrollTop = scrollContainer.scrollHeight;
                }, 1)
            }

        },
        initDeleteTaskConfirmationModal() {
            const element = document.getElementById("delete-task-confirmation-modal");
            this.$store.taskModal.deleteModalHandle = new bootstrap.Modal(element);
            const cleanup = () => { };
            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener("hidden.bs.modal", cleanup);
        },
        openDeleteModal(e) {
            console.log('task open delete event ? :', e)
            console.log('open delete modal')
            const task = e.detail
            this.$store.taskModal.onDeleteClick(task)
            this.currentDeletingTask = task;
            console.log(this.currentDeletingTask);
        },
        //feedback
        initFeedbackModal() {
            console.log('init feedback modal ?')
            const element = document.getElementById("feedback-modal");
            this.$store.taskModal.feedbackModalHandle = new bootstrap.Modal(element);
            const cleanup = () => {
                this.feedbackStatus = 3;
                this.feedbackComment = '';
                this.currentFeedbackTask = null;
            }
            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener("hidden.bs.modal", cleanup);
        },
        openFeedbackModal(e) {
            console.log('task open feedback event ? :', e)
            const task = e.detail
            console.log('task open feedback modal ? :', task)
            this.currentFeedbackTask = task;
            this.$store.taskModal.onFeedbackClick(task)
        },
        async onSubmitFeedback() {
            await this.$store.task.issueFollowup(this.currentFeedbackTask, this.feedbackStatus, this.feedbackComment)
            // await this.getData();
            this.feedbackStatus = 3;
            this.feedbackComment = '';
            this.currentFeedbackTask = null;
            this.$store.taskModal.feedbackModalHandle.hide();
            await this.$store.tasksData.getTasks()
        },
    }
}

Alpine.data("TaskModal", TaskModal)
