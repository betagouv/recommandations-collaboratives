import Alpine from 'alpinejs';
import { Toast } from 'bootstrap';

Alpine.data('Toast', () => {
  return {
    init() {
      const toastContainer = this.$refs.toastContainer;
      new Toast(toastContainer).show();
    },
  };
});
