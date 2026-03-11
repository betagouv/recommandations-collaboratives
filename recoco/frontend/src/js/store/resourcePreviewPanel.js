import Alpine from 'alpinejs';

Alpine.store('resourcePreviewPanel', {
  isOpen: false,
  recommendation: null,
  message: null,
  messageId: null,

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
    window.dispatchEvent(new CustomEvent('on-click-handle-reply', { detail: this.messageId }));
    this.scrollToMessage();
  },
});

export default Alpine.store('resourcePreviewPanel');
