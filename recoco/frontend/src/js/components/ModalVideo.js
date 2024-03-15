import Alpine from 'alpinejs';
import {Modal} from 'bootstrap';

function ModalVideo() {
  return {
    initHomeVideoModal() {
      const element = document.getElementById('home-video-modal');
      this.homeVideoModal = new Modal(element);

      const cleanup = () => {
        this.$refs.video.src = '';
        this.$refs.video.src = 'https://www.youtube.com/embed/HiAq3VhuMzo';
      };

      element.addEventListener('hidePrevented.bs.modal', cleanup);
      element.addEventListener('hidden.bs.modal', cleanup);
    },
    openHomeVideoModal() {
      this.homeVideoModal.show();
    },
  };
}

Alpine.data('ModalVideo', ModalVideo);
