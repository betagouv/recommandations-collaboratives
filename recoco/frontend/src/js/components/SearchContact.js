import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';

function SearchContact() {
  return {
    init() {
     console.log('coucou');
    },
    initSearchContactModal() {
      const element = document.getElementById('search-contact-modal');
      this.searchContactModal = new Modal(element);
    },
    openSearchContactModal() {
      this.searchContactModal.show();
    },
  };
}

Alpine.data('SearchContact', SearchContact);
