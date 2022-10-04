import Alpine from 'alpinejs'
import { STATUSES, isStatus } from '../utils/tasks'

function StatusSwitcher(commentTextRef, commentTextFormRef) {
    return {
        STATUSES,
        activeStatus(task, status) {
            return isStatus(task, status) ? "active" : undefined
        },
        async handleStatusClick(task, status) {
            this.$dispatch('issue-followup', { task, status })
        },
        async handleStatusWithCommentClick(task, status) {
            location.href = "#modal-textarea";
            commentTextRef.classList.add('textarea-highlight');
            commentTextFormRef.classList.add('tooltip-highlight');
            this.$dispatch('issue-followup', { task, status })
        }
    }
}

Alpine.data("StatusSwitcher", StatusSwitcher)
