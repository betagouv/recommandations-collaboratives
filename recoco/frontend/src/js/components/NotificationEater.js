import Alpine from 'alpinejs';
import api, {
  conversationsMessageMarkAsReadUrl,
  markTaskNotificationAsVisited,
} from '../utils/api';
const MIN_TIME_MS = 1000;
const MAX_TIME_MS = 15000;

Alpine.data('NotificationEater', (projectId) => {
  return {
    projectId: projectId,
    init() {
      const messageMap = new Map();

      requestAnimationFrame(() => {
        // Consumption logic run after 5sec on the page
        setTimeout(() => {
          const observer = new IntersectionObserver(
            (entries) => {
              entries.forEach((entry) => {
                const elementId = entry.target.getAttribute('data-element-id');
                if (entry.isIntersecting) {
                  const messageData = JSON.parse(
                    entry.target.getAttribute('data-notifications')
                  );

                  if (messageData.unread === 0) return;

                  // Run a timer to consume notification based on the message length
                  const timerId = setTimeout(() => {
                    this.consumeNotification(messageData, entry.target);
                  }, this.getTimeToReadMessage(messageData.charNum));

                  messageMap.set(elementId, timerId);
                } else {
                  // If the message go out of screen before the consumption clear the timer
                  clearTimeout(messageMap.get(elementId));
                }
              });
            },
            { rootMargin: '-150px' }
          );
          const observedElements =
            document.querySelectorAll('.observed-element');
          observedElements.forEach((el) => observer.observe(el));
        }, 5000);

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
    getNumCharInMessage(message) {
      const filteredContentToCount = message.nodes.filter(
        (x) => x.type === 'MarkdownNode' || x.type === 'RecommendationNode'
      );

      return filteredContentToCount
        .map((x) => x.text.length)
        .reduce((a, b) => a + b, 0);
    },
    getTimeToReadMessage(messageLength) {
      const CHAR_READ_PER_MIN = 1200;

      const timeMs = (messageLength / CHAR_READ_PER_MIN) * 60 * 1000;
      return Math.max(MIN_TIME_MS, Math.min(MAX_TIME_MS, timeMs));
    },
    async consumeNotification(message, messageElement) {
      try {
        const responseConsumedRecommendation =
          await this.consumeRecommendationNotification(message.id);

        if (
          responseConsumedRecommendation.recommendationWithRessource ||
          responseConsumedRecommendation.noMessage
        ) {
          return;
        }

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
      } catch (error) {
        throw new Error('Failed to consume notification', error);
      }
    },
    async consumeRecommendationNotification(id) {
      const response = {
        noMessage: false,
        noRecommendation: false,
        noRessource: false,
        recommendationWithRessource: false,
      };
      const parentFeed = Alpine.$data(this.$el.parentElement).feed;
      const parentTasks = Alpine.$data(this.$el.parentElement).tasks;
      const foundMessage = parentFeed.messages.find(
        (message) => message.id == id
      );
      if (!foundMessage) {
        response.noMessage = true;
        return response;
      }
      const foundRecommendation = foundMessage.nodes.find(
        (node) => node.type == 'RecommendationNode'
      );
      if (!foundRecommendation) {
        response.noRecommendation = true;
        return response;
      }
      const foundTask = parentTasks.find(
        (task) => task.id == foundRecommendation.recommendation_id
      );
      if (!foundTask) {
        response.noRecommendation = true;
        return response;
      }
      if (foundTask.resource) {
        response.recommendationWithRessource = true;
        return response;
      }

      try {
        await api.post(
          markTaskNotificationAsVisited(
            this.projectId,
            foundRecommendation.recommendation_id
          )
        );
        response.noRessource = true;
        return response;
      } catch (error) {
        throw new Error('Failed to consume recommendation notification', error);
      }
    },
  };
});
