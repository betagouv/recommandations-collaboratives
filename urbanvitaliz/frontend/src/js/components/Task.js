import Alpine from 'alpinejs'

import{ editTaskUrl, deleteTaskReminderUrl} from '../utils/api'

import { TASK_STATUSES } from '../config/statuses';
import { formatReminderDate, daysFromNow, formatDate } from '../utils/date'
import { toArchiveTooltip, reminderTooltip, isOldReminder } from '../utils/tooltip'
import { renderMarkdown } from '../utils/markdown'
import { gravatar_url } from '../utils/gravatar'

export default function Task(currentTask) {
    return {
        currentTask:null,
        currentTaskId:null,
        toArchiveTooltip,
        currentTaskFollowups:null,
        currentTaskNotifications:null,
        editTaskUrl,
        renderMarkdown,
        formatDate,
        gravatar_url,
        isOldReminder,
        reminderTooltip,
        deleteTaskReminderUrl,
        init() {
            this.currentTask = currentTask
        },
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
        handleOpenPreviewModal(task) {
            console.log('dispatch somthg', task);
            console.log(this.$dispatch('open-preview-modal', task))
            console.log(this.$dispatch('issue-followup', { task }))
        },
        // Feedback
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
         // Comments
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
        truncate(input, size = 30) {
            return input.length > size ? `${input.substring(0, size)}...` : input;
        },
        formatDateDisplay(date) {
            return new Date(date).toLocaleDateString('fr-FR');
        },
    }
}

Alpine.data("Task", Task)
