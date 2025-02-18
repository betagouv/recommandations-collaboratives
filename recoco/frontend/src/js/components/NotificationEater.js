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
      setTimeout(() => {
        this.hideScrollLine();
        this.scrollToFirstNotification();
        console.log('scroll init');
      }, 500);
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
        console.log('scrollLineNewNotification not found');

        window.scroll({
          top: document.body.scrollHeight,
          behavior: 'instant',
        });
      }
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
    consumeNotifiction(notificationId) {
      api.patch(notificationsMarkAsReadByIdUrl(notificationId));
    },
  };
});
