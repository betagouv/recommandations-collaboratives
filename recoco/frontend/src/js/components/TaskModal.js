import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';
import { TASK_STATUSES } from '../config/statuses';

import { renderMarkdown } from '../utils/markdown';
import { formatDate } from '../utils/date';
import { resourcePreviewUrl, deleteTaskUrl } from '../utils/api';
import { gravatar_url } from '../utils/gravatar';
import {
  isStatusUpdate,
  statusText,
  isArchivedStatus,
} from '../utils/taskStatus';

export default function TaskModal() {
  return {
    currentlyEditing: null,
    pendingComment: '',
    renderMarkdown,
    formatDate,
    resourcePreviewUrl,
    gravatar_url,
    currentTaskFollowups: [],
    currentTaskNotifications: [],
    isStatusUpdate,
    statusText,
    deleteTaskUrl,
    currentDeletingTask: {},
    feedbackComment: '',
    DONE_STATUS: TASK_STATUSES.DONE,
    isArchivedStatus,
    initDeleteTaskConfirmationModal() {
      const element = document.getElementById('delete-task-confirmation-modal');
      this.$store.taskModal.deleteModalHandle = new Modal(element);
      const cleanup = () => {};
      element.addEventListener('hidePrevented.bs.modal', cleanup);
      element.addEventListener('hidden.bs.modal', cleanup);
    },
    openDeleteModal(e) {
      const task = e.detail;
      this.$store.taskModal.onDeleteClick(task);
      this.currentDeletingTask = task;
    },
  };
}

Alpine.data('TaskModal', TaskModal);
