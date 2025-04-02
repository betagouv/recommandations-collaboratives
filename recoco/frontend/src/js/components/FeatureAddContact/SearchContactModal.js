import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../../utils/api';
import { Modal } from '../../models/modal';

Alpine.data('SearchContactModal', () => ({
  Modal: null,
  contactsFound: [],
  userInput: '',
  selectedContact: null,
  delayDisplay: false,
  modalCreateContact: null,
  modalSearchContact: null,
  isVisible: false,
  noSearch: true,
  init() {
    this.Modal = Modal(this);
  },
  onSearch() {
    this.delayDisplay = true;
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
  isModalCreateContactOpen: false,
  openModalCreateContact() {
    // hide search contact modal
    this.modalSearchContact = this.$refs.searchContactModal;
    this.modalSearchContact.classList.toggle('d-none');
    // create contact modal
    this.isModalCreateContactOpen = true;
  },
  closeModalCreateContact() {
    this.isModalCreateContactOpen = false;
    this.modalSearchContact.classList.toggle('d-none');
  },
}));
