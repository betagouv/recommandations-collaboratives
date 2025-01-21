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
      window.scroll({
        top: this.$refs.scrollLine.offsetTop - 260,
        behavior: 'smooth',
      });
    },
    hideScrollLine() {
      document.querySelectorAll('[x-ref="scrollLine"]').forEach((el, i) => {
        if (i == 1) return;
        el.classList.add('d-none');
      });
    },
  };
});
