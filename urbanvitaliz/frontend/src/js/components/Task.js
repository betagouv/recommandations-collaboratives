import Alpine from 'alpinejs'

import{ editTaskUrl, deleteTaskReminderUrl} from '../utils/api'

import { TASK_STATUSES } from '../config/statuses';
import { formatReminderDate, daysFromNow, formatDate } from '../utils/date'
import { isStatusUpdate, statusText, isArchivedStatus } from "../utils/taskStatus"
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
            console.log('Task init ?')
            this.currentTask = currentTask
            console.log('current task  :', currentTask);
        },
        hasNotification(followupId) {
            return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
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

            if (isMember && !isHijacked) await patchTask(this.currentTaskId, { visited: true });

            await markAllAsRead(this.currentTaskId);

            this.followupScrollToLastMessage();

            await this.getData();
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
            this.followupScrollToLastMessage();
        },
        truncate(input, size = 30) {
            return input.length > size ? `${input.substring(0, size)}...` : input;
        },
        formatDateDisplay(date) {
            return new Date(date).toLocaleDateString('fr-FR');
        },
        followupScrollToLastMessage() {
            const scrollContainer = document.getElementById("followups-scroll-container");
            if (scrollContainer) scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
    }
}

Alpine.data("Task", Task)
