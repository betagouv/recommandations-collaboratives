import Alpine from 'alpinejs';

document.addEventListener('alpine:init', () => {
  Alpine.store('resourcePreviewPanel', {
    isOpen: false,
    recommendation: null,
    message: null,
    messageId: null,
    _unsubscribe: null,

    init() {
      // Subscribe to tasksData changes to keep recommendation in sync
      const tasksData = Alpine.store('tasksData');
      if (tasksData && tasksData._subscribe) {
        this._unsubscribe = tasksData._subscribe(() => {
          if (this.isOpen && this.recommendation) {
            // Find the updated task in tasksData
            const updatedTask = tasksData.getTaskById(this.recommendation.id);
            if (updatedTask) {
              // Update the recommendation status while preserving other properties
              this.recommendation.status = updatedTask.status;
              this.recommendation.visited = updatedTask.visited;
            }
          }
        });
      }
    },

    open(recommendation, message) {
      this.recommendation = recommendation;
      this.recommendation.created_by.id = message.posted_by;
      this.message = message;
      this.messageId = message?.id;
      this.isOpen = true;

      // Prevent body scroll when panel is open
      document.body.style.overflow = 'hidden';
    },

    close() {
      this.isOpen = false;
      this.recommendation = null;
      this.message = null;
      this.messageId = null;

      // Restore body scroll
      document.body.style.overflow = '';
    },

    scrollToMessage() {
      const messageId = this.messageId;
      this.close();

      // Scroll to the original message after panel closes
      if (messageId) {
        Alpine.nextTick(() => {
          const messageElement = document.getElementById(`message-${messageId}`);
          if (messageElement) {
            messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Highlight the message briefly
            messageElement.classList.add('highlight-message');
            setTimeout(() => {
              messageElement.classList.remove('highlight-message');
            }, 2000);
          }
        });
      }
    },


    replyToMessage() {
      window.dispatchEvent(
        new CustomEvent('on-click-handle-reply', { detail: this.messageId })
      );
      this.scrollToMessage();
    },
  });
});

export default Alpine.store('resourcePreviewPanel');
