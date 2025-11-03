import Alpine from 'alpinejs';
import api, {
  conversationsMessageMarkAsReadUrl,
  markTaskNotificationAsVisited,
} from '../utils/api';

Alpine.data('NotificationEater', (projectId) => {
  return {
    projectId: projectId,
    init() {
      requestAnimationFrame(() => {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                const messageData = JSON.parse(
                  entry.target.getAttribute('data-notifications')
                );
                if (messageData.unread === 0) return;
                this.consumeNotification(messageData, entry.target);
              }
            });
          },
          { rootMargin: '-150px' }
        );
        const observedElements = document.querySelectorAll('.observed-element');
        observedElements.forEach((el) => observer.observe(el));
        setTimeout(() => {
          this.hideScrollLine();
          const params = new URLSearchParams(document.location.search);
          const messageId = parseInt(params.get('message-id'));
          if (messageId) {
            this.scrollToMessage(messageId);
          } else {
            this.scrollToFirstNotification();
          }
        }, 500);
      });
    },

    scrollToMessage(messageId) {
      const message = document.getElementById(`message-${messageId}`);
      if (message) {
        const elementPosition =
          message.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - 150;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth',
        });
      }
    },
    scrollToFirstNotification(topic) {
      if (topic?.detail) topic = topic.detail;
      this.hideScrollLine(topic);
      let scrollLineNewNotification = document.querySelectorAll(
        `[x-ref="scrollLine_${topic}"]`
      );

      if (scrollLineNewNotification.length == 0) {
        scrollLineNewNotification = document.querySelectorAll(
          `[x-ref^="scrollLine_"]`
        );
      }

      if (scrollLineNewNotification.length > 0) {
        window.scroll({
          top: scrollLineNewNotification[0].offsetTop - 260,
          behavior: 'instant',
        });
      } else {
        window.scroll({
          top: document.body.scrollHeight,
          behavior: 'instant',
        });
      }
    },
    addScrollLine() {
      const scrollLine = document.createElement('div');
      scrollLine.classList.add('scroll-line');
      scrollLine.setAttribute('x-ref', `scrollLine_${topic}`);
      document.body.appendChild(scrollLine);
    },
    hideScrollLine(topic) {
      let scrollLineNewNotification = document.querySelectorAll(
        `[x-ref="scrollLine_${topic}"]`
      );
      if (scrollLineNewNotification.length == 0) {
        scrollLineNewNotification = document.querySelectorAll(
          `[x-ref^="scrollLine_"]`
        );
      }
      if (scrollLineNewNotification.length == 0) return;
      scrollLineNewNotification[0].classList.remove('d-none');
    },
    async consumeNotification(message, messageElement) {
      try {
        await api.post(
          conversationsMessageMarkAsReadUrl(this.projectId, message.id)
        );

        messageElement.setAttribute(
          'data-notifications',
          JSON.stringify({
            ...message,
            unread: 0,
          })
        );
        await this.consumeRecommendationNotification(message.id);
      } catch (error) {
        throw new Error('Failed to consume notification', error);
      }
    },
    async consumeRecommendationNotification(id) {
      const parentFeed = Alpine.$data(this.$el.parentElement).feed;
      const foundMessage = parentFeed.messages.find(
        (message) => message.id == id
      );
      if (!foundMessage) {
        return null;
      }
      const foundRecommendation = foundMessage.nodes.find(
        (node) => node.type == 'RecommendationNode'
      );
      if (!foundRecommendation) {
        return null;
      }
      try {
        await api.post(
          markTaskNotificationAsVisited(
            this.projectId,
            foundRecommendation.recommendation_id
          )
        );
      } catch (error) {
        throw new Error('Failed to consume recommendation notification', error);
      }
    },
  };
});
