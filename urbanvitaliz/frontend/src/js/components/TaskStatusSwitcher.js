import Alpine from 'alpinejs'
import { STATUSES, isStatus, statusText } from '../utils/tasks'

function TaskStatusSwitcher(commentTextRef, commentTextFormRef) {
    return {
        STATUSES,
        statusText,
        handleStatusWrapper() {
            return this.openStatusWrapper = !this.openStatusWrapper
        },
        activeStatus(task, status) {
            return isStatus(task, status) ? "active" : undefined
        },
        async handleStatusClick(task, status) {
            task.isLoading = true
            await this.$store.tasksData.issueFollowup(task, status);
            await this.$store.tasksView.updateViewWithTask(task.id)
            task.isLoading = false
        },
        // async handleStatusWithCommentClick(task, status) {
        //     location.href = "#modal-textarea";
        //     commentTextRef.classList.add('textarea-highlight');
        //     commentTextFormRef.classList.add('tooltip-highlight');
        //     this.$dispatch('issue-followup', { task, status })
        // }
    }
}

Alpine.data("TaskStatusSwitcher", TaskStatusSwitcher)
