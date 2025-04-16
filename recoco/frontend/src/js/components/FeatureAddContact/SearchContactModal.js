import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';
import { formatDate } from '../../utils/date';

Alpine.data('SearchContactModal', () => ({
  Modal: null,
  formatDate,
  contactsFound: [],
  userInput: '',
  selectedContact: null,
  modalCreateContact: null,
  modalSearchContact: null,
  noSearch: true,
  init() {
    this.Modal = Modal(this, 'search-contact-modal');
  },
  onSearch() {
    this.noSearch = false;
    this.selectedContact = null;
    if (this.userInput.length > 0) {
      api.get(searchContactsUrl(this.userInput)).then((response) => {
        const searchResults = response.data;
        this.contactsFound = searchResults.results;
      });
    } else if (this.userInput.length === 0) {
      this.noSearch = true;
    }
  },
  onSelect(contact) {
    this.noSearch = false;
    this.selectedContact = contact;
  },
  addContact() {
    this.Modal.responseModal(this.selectedContact);
  },
  onCancelSelectContact() {
    this.selectedContact = null;
  },
  isCreateContactModalOpen: false,
  openModalCreateContact() {
    // hide search contact modal
    this.modalSearchContact = this.$refs.searchContactModal;
    this.modalSearchContact.classList.toggle('d-none');
    // create contact modal
    this.isCreateContactModalOpen = true;
  },
  closeCreateContactModal(event) {
    if (event.target.id !== 'create-contact-modal') {
      return;
    }
    if (event.detail) {
      this.onSelect(event.detail);
    }
    this.isCreateContactModalOpen = false;
    this.modalSearchContact.classList.toggle('d-none');
  },
}));
