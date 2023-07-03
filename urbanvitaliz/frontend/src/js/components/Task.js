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
            this.currentTask = currentTask
        },

        handleOpenPreviewModal() {
            console.log('dispatch somthg', this.currentTask);
            console.log(this.$dispatch('open-preview-modal', this.currentTask))
        },
        handleOpenDeleteModal() {
            console.log('dispatch somthg', this.currentTask);
            console.log(this.$dispatch('open-delete-modal', this.currentTask))
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
