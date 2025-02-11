import Alpine from 'alpinejs';
import api, { notificationsMarkAsReadByIdUrl } from '../utils/api';

Alpine.data('NotificationEater', (projectId) => {
  return {
    projectId: projectId,
    init() {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const notificationIdToConsume = JSON.parse(
                entry.target.getAttribute('data-notifications')
              )[0];
              if (!notificationIdToConsume) return;
              this.consumeNotifiction(notificationIdToConsume);
            }
          });
        },
        { rootMargin: '-150px' }
      );
      const observedElements = document.querySelectorAll('.observed-element');
      observedElements.forEach((el) => observer.observe(el));
      this.hideScrollLine();
      document.addEventListener('alpine:initialized', () => {
        this.scrollToFirstNotification();
      });
    },
    scrollToFirstNotification(topic = 'general') {
      if (topic.detail) topic = topic.detail;
      this.hideScrollLine(topic);
      let scrollLineNewNotification = document.querySelectorAll(
        `[x-ref="scrollLine_${topic}"]`
      );

      if (scrollLineNewNotification.length == 0) {
        scrollLineNewNotification = document.querySelectorAll(
          `[x-ref^="scrollLine"]`
        );
      }
      if (scrollLineNewNotification.length > 0) {
        window.scroll({
          top: scrollLineNewNotification[0].offsetTop - 260,
          behavior: 'instant',
        });
      } else {
        window.scroll({
          top: this.$refs[`scrollLineLastMessage_${topic}`].offsetTop,
          behavior: 'instant',
        });
      }
    },
    hideScrollLine(topic) {
      const scrollLineNewNotification = document.querySelectorAll(
        `[x-ref="scrollLine_${topic}"]`
      );
      scrollLineNewNotification.forEach((el, i) => {
        if (i == 0) return;
        el.classList.add('d-none');
      });
    },
    consumeNotifiction(notificationId) {
      api.patch(notificationsMarkAsReadByIdUrl(notificationId));
    },
  };
});
