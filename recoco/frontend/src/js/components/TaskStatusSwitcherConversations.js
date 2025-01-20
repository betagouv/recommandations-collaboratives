import Alpine from 'alpinejs';
import api, { followupsUrl } from '../utils/api';
import {
  STATUSES,
  isStatus,
  statusText,
  isArchivedStatus,
} from '../utils/taskStatus';

Alpine.data('TaskStatusSwitcherConversations', function (projectId, task) {
  return {
    task: task,
    projectId: projectId,
    STATUSES,
    statusText,
    handleStatusWrapper() {
      return (this.openStatusWrapper = !this.openStatusWrapper);
    },
    activeStatus(status) {
      return isStatus(this.task, status) ? 'active' : undefined;
    },
    async handleStatusClick(status) {
      this.task.isLoading = true;

      if (status === STATUSES.DONE || isArchivedStatus(status)) {
        this.$dispatch('open-feedback-modal', { task: task, status: status });
      } else {
        if (status === task.status) return;
        await api.post(followupsUrl(this.projectId, task.id), {
          status,
          comment: '',
        });
      }

      await this.$store.tasksView.updateViewWithTask(task.id);
      task.isLoading = false;
    },
  };
});
