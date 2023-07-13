import Alpine from 'alpinejs'
import { TASK_STATUSES } from '../config/statuses';

import { renderMarkdown } from '../utils/markdown'
import { formatDate } from '../utils/date'
import { resourcePreviewUrl, deleteTaskUrl } from '../utils/api'
import { gravatar_url } from '../utils/gravatar'
import { isStatusUpdate, statusText } from "../utils/taskStatus"

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
        //Event listener dispatched by another component
        async handleIssueFollowup(e) {
            await this.$store.tasksData.issueFollowup(e.detail.task, e.detail.status)
            // await this.getData()
        },
        initDeleteTaskConfirmationModal() {
            const element = document.getElementById("delete-task-confirmation-modal");
            this.$store.taskModal.deleteModalHandle = new bootstrap.Modal(element);
            const cleanup = () => { };
            element.addEventListener("hidePrevented.bs.modal", cleanup);
            element.addEventListener("hidden.bs.modal", cleanup);
        },
        openDeleteModal(e) {
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
            await this.$store.tasksData.issueFollowup(this.currentFeedbackTask, this.feedbackStatus, this.feedbackComment)
            // await this.getData();
            this.feedbackStatus = 3;
            this.feedbackComment = '';
            this.currentFeedbackTask = null;
            this.$store.taskModal.feedbackModalHandle.hide();
            await this.$store.tasksView.updateView()
        },
    }
}

Alpine.data("TaskModal", TaskModal)
