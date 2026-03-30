import Alpine from 'alpinejs';
import {
  STATUSES,
  isStatus,
  statusText,
} from '../utils/taskStatus';

Alpine.data('TaskStatusSwitcherConversations', function (projectId, task) {
  return {
    taskId: task.id,
    projectId: projectId,
    isLoading: false,
    STATUSES,
    statusText,

    get task() {
      const storeTask = Alpine.store('tasksData').getTaskById(this.taskId);
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
        await this.$store.tasksData.issueFollowup(this.task, status);
        await this.$store.tasksView.updateViewWithTask(this.taskId);
      } catch (error) {
        throw new Error('Failed to update task status');
      }

      this.isLoading = false;
    },
  };
});
