import Alpine from 'alpinejs';
import { STATUSES, isStatus, statusText } from '../utils/taskStatus';

function TaskStatusSwitcher(task) {
  return {
    STATUSES,
    statusText,
    handleStatusWrapper() {
      return (this.openStatusWrapper = !this.openStatusWrapper);
    },
    activeStatus(task, status) {
      return isStatus(task, status) ? 'active' : undefined;
    },
    async handleStatusClick(task, status) {
      task.isLoading = true;
      await this.$store.tasksData.issueFollowup(task, status);
      await this.$store.tasksView.updateViewWithTask(task.id);
      task.isLoading = false;
      task.status = status;
    },
  };
}

Alpine.data('TaskStatusSwitcher', TaskStatusSwitcher);
