import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('SearchContactModal', () => ({
  Modal: null,
  contactsFound: [],
  userInputSearchContact: '',
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
    if (this.userInputSearchContact.length > 0) {
      try {
        api.get(searchContactsUrl(this.userInputSearchContact)).then((response) => {
          const searchResults = response.data;
          this.contactsFound = searchResults.results;
        });
      } catch (error) {
          console.log(error);
        }
    } else if (this.userInputSearchContact.length === 0) {
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
    if (this.userInputSearchContact.length === 0) {
      this.noSearch = true;
    }
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
      console.log('event.detail', event.detail);
    }
    this.isCreateContactModalOpen = false;
    this.modalSearchContact.classList.toggle('d-none');
  },
}));
