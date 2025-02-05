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
      this.scrollToFirstNotification();
    },
    scrollToFirstNotification(topic = 'general') {
      const scrollLine = document.querySelectorAll('[x-ref="scrollLine"]');
      let scrollTo = this.$refs[`scrollLineLastMessage_${topic}`];
      if (scrollLine.length > 0) {
        scrollTo = scrollLine[0];
      }

      window.scroll({
        top: scrollTo.offsetTop - 260,
        behavior: 'smooth',
      });
    },
    hideScrollLine() {
      const scrollLine = document.querySelectorAll('[x-ref="scrollLine"]');
      scrollLine.forEach((el, i) => {
        if (i == 0) return;
        el.classList.add('d-none');
      });
    },
    consumeNotifiction(notificationId) {
      api.patch(notificationsMarkAsReadByIdUrl(notificationId));
    },
  };
});
