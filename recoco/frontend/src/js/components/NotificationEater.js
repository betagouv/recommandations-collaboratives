import Alpine from 'alpinejs';
import api, { notificationsMarkAsReadByIdUrl } from '../utils/api';

Alpine.data('NotificationEater', (projectId) => {
  return {
    projectId: projectId,
    init() {
      requestAnimationFrame(() => {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                const elementToConsume = JSON.parse(
                  entry.target.getAttribute('data-notifications')
                );
                console.log('elementToConsume', elementToConsume);
                if (elementToConsume.read) return;
                this.consumeNotifiction(elementToConsume.id);
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
        }, 500);
      });
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
    consumeNotifiction(notificationId) {
      // TODO **********************
      // TODO udpate this endpoint to accept the type of the element to consume
      // TODO wait for backend to be ready
      // TODO **********************
      // api.patch(notificationsMarkAsReadByIdUrl(notificationId));
    },
  };
});
