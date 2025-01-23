import Alpine from 'alpinejs';
import api from '../utils/api';

Alpine.data('NotificationEater', () => {
  return {
    init() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            console.log('====================================');
            console.log('NotificationEater', entry.target.getAttribute('data'));
            console.log('====================================');
          }
        });
      });
      const observedElements = document.querySelectorAll('.observed-element');
      observedElements.forEach((el) => observer.observe(el));
      this.hideScrollLine();
      this.scrollToFirstNotification();
    },
    scrollToFirstNotification() {
      const scrollLine = document.querySelectorAll('[x-ref="scrollLine"]');
      let scrollTo = this.$refs.scrollLineLastMessage;
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
  };
});
