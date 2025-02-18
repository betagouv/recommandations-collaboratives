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

      if (status === task.status) return;
      try {
        await api.post(followupsUrl(this.projectId, task.id), {
          status,
          comment: '',
        });
        this.task.status = status;
      } catch (error) {
        throw new Error('Failed to update task status');
      }

      this.task.isLoading = false;
    },
  };
});
