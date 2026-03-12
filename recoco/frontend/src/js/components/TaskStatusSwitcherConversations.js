import Alpine from 'alpinejs';
import {
  STATUSES,
  isStatus,
  statusText,
  isArchivedStatus,
} from '../utils/taskStatus';

Alpine.data('TaskStatusSwitcherConversations', function (projectId, task) {
  return {
    taskId: task.id,
    projectId: projectId,
    isLoading: false,
    STATUSES,
    statusText,

    // Get fresh task data from the store
    get task() {
      const storeTask = this.$store.tasksData.getTaskById(this.taskId);
      return storeTask || { id: this.taskId, status: task.status };
    },

    handleStatusWrapper() {
      return (this.openStatusWrapper = !this.openStatusWrapper);
    },
    activeStatus(status) {
      return isStatus(this.task, status) ? 'active' : undefined;
    },
    async handleStatusClick(status) {
      if (status === this.task.status) return;

      this.isLoading = true;

      try {
        // Use the central tasksData store to issue the followup
        // This ensures all subscribers (including the tasks panel) are notified
        await this.$store.tasksData.issueFollowup(this.task, status);

        // Update tasksView.displayedTasks to sync the tasks panel
        // This calls loadTasks() internally and updates the displayed tasks
        await this.$store.tasksView.updateViewWithTask(this.taskId);
      } catch (error) {
        throw new Error('Failed to update task status');
      }

      this.isLoading = false;
    },
  };
});
