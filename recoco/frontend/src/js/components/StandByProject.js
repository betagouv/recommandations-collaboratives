import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';

function StandByProject() {
  return {
    initStandByProjectConfirmationModal() {
      const element = document.getElementById(
        'stand-by-project-confirmation-modal'
      );
      this.StandByProjectConfirmationModal = new Modal(element);
    },
    openStandByProjectConfirmationModal() {
      this.StandByProjectConfirmationModal.show();
    },
  };
}

Alpine.data('StandByProject', StandByProject);
