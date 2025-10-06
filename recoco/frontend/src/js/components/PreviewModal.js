import Alpine from 'alpinejs';
import { resourcePreviewUrl } from '../utils/api';
import { renderMarkdown } from '../utils/markdown';
// import { formatDate } from '../utils/date';
// import { gravatar_url } from '../utils/gravatar';
// import { isStatusUpdate, statusText } from '../utils/taskStatus';
import { truncate } from '../utils/taskStatus';
/**
 * A Preview Modal component
 */
export default function PreviewModal() {
  return {
    showEdition: false,

    get index() {
      return this.$store.previewModal.index;
    },
    get taskId() {
      return this.$store.previewModal.taskId;
    },
    get currentTask() {
      return this.$store.tasksData.getTaskById(this.taskId);
    },
    get notifications() {
      return this.$store.previewModal.notifications;
    },
    get newTasks() {
      return this.$store.tasksData.newTasks;
    },
    resourcePreviewUrl,
    renderMarkdown,
    // formatDate,
    // gravatar_url,
    // isStatusUpdate,
    // statusText,
    truncate,
    newTasksNavigationText() {
      return `${this.index + 1} sur ${this.newTasks.length} nouvelle${this.newTasks.length > 0 ? 's' : ''} recommandation${this.newTasks.length > 0 ? 's' : ''}`;
    },
    hasNotification(followupId) {
      if (this.notifications) return false;

      return (
        this.notifications.filter(
          (n) => n.action_object.who && n.action_object.id === followupId
        ).length > 0
      );
    },
    // Close the modal
    changeShowEdition() {
      this.showEdition = false;
    },
    //add a class to adapt the modal size depending on the content
    getTypeOfModalClass(isDocumented) {
      let typeOfModalClass = '';

      if (this.$store.previewModal.isPaginated) {
        typeOfModalClass = 'is-paginated';
      }

      if (isDocumented) {
        typeOfModalClass = 'is-documented';
      }

      if (this.$store.previewModal.isPaginated && isDocumented) {
        typeOfModalClass = 'is-paginated-documented';
      }

      return typeOfModalClass;
    },
  };
}

Alpine.data('PreviewModal', PreviewModal);
