import Alpine from 'alpinejs';
import { resourcePreviewUrl } from '../utils/api';
import { renderMarkdown } from '../utils/markdown';
import { formatDate } from '../utils/date';
import { gravatar_url } from '../utils/gravatar';
import { isStatusUpdate, statusText } from '../utils/taskStatus';
import { truncate } from '../utils/taskStatus';
import { tiptapParserJSONToHTML } from '../utils/tiptapParser';
/**
 * A Preview Modal component
 */
export default function PreviewModal() {
  return {
    currentlyEditing: null,
    followupsIsLoading: false,
    contentIsLoading: false,
    showEdition: false,

    comment: {
      text: '',
      contact: '',
    },

    get index() {
      return this.$store.previewModal.index;
    },
    get taskId() {
      return this.$store.previewModal.taskId;
    },
    get currentTask() {
      return this.$store.tasksData.getTaskById(this.taskId);
    },
    get followups() {
      return this.$store.previewModal.followups;
    },
    get notifications() {
      return this.$store.previewModal.notifications;
    },
    get newTasks() {
      return this.$store.tasksData.newTasks;
    },
    async refresh() {
      this.followupScrollToLastMessage();
    },
    resourcePreviewUrl,
    renderMarkdown,
    tiptapParserJSONToHTML,
    formatDate,
    gravatar_url,
    isStatusUpdate,
    statusText,
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
    async onSubmitComment() {
      this.$store.editor.setIsSubmitted(true);

      // We are not editing a comment atm
      if (!this.currentlyEditing) {
        await this.$store.tasksData
          .issueFollowup(
            this.currentTask,
            undefined,
            this.comment.text,
            this.comment.contact ?? null
          )
          .then(async () => {
            // Refresh messages
            await this.$store.previewModal.loadFollowups();
            await this.$store.tasksView.updateView();
            // reset every contact info after submitting
            this.comment.contact = '';
            this.comment.text = '';
          })
          .catch((error) => {
            console.error('Error while creating followup', error);
          });
      } else {
        // We are editing a comment
        const [type, id] = this.currentlyEditing;
        if (type === 'followup') {
          this.followupsIsLoading = true;
          await this.$store.tasksData.editComment(this.currentTask.id, id, {
            comment: this.comment.text,
            contact: this.comment.contact,
          });
          await this.$store.previewModal.loadFollowups();
          await this.$store.tasksView.updateView();
          this.followupsIsLoading = false;
        } else if (type === 'content') {
          // We are editing the initial comment (contained in Task model)
          await this.$store.tasksData.patchTask(this.currentTask.id, {
            content: this.comment.text,
            contact: this.comment.contact,
          });
          await this.$store.tasksView.updateViewWithTask(this.currentTask.id);
        }
      }
      this.currentlyEditing = null;
      this.$dispatch('set-comment', { text: '', contact: null });
      this.followupScrollToLastMessage();
      if (!this.currentTask.public) {
        this.showEdition = false;
      }
    },
    onEditComment(followup) {
      this.showEdition = true;
      this.currentlyEditing = ['followup', followup.id];
      document.querySelector('#comment-text-ref .ProseMirror').focus();
      this.$dispatch('set-comment', {
        text: followup.comment,
        contact: followup.contact,
      });
    },
    onEditContent() {
      this.showEdition = true;
      this.currentlyEditing = ['content', this.currentTask.id];
      document.querySelector('#comment-text-ref .ProseMirror').focus();
      this.$dispatch('set-comment', {
        text: this.currentTask.content,
        contact: this.currentTask.contact,
      });
    },
    onCancelEdit() {
      this.showEdition = false;
      this.currentlyEditing = null;
      this.$dispatch('set-comment', { text: '', contact: null });
    },
    loadContent() {
      this.contentIsLoading = true;
      setTimeout(() => {
        this.contentIsLoading = false;
      }, 300);
    },
    followupScrollToLastMessage(initPage = false) {
      if (initPage) {
        this.followupsIsLoading = true;
      }

      const scrollContainer = document.getElementById(
        'followups-scroll-container'
      );
      if (scrollContainer) {
        setTimeout(
          () => {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;

            if (initPage) {
              this.followupsIsLoading = false;
            }
          },
          initPage ? 500 : 1
        );
      }
    },
    changeShowEdition() {
      this.showEdition = false;
    },

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
