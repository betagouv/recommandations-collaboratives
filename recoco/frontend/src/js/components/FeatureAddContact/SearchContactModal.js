import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../../utils/api';
import { Modal } from '../../models/modal';

Alpine.data('SearchContactModal', () => ({
  Modal: null,
  searchResults: [],
  contactsFound: [],
  isOpenModal: false,
  userInput: '',
  showContactsresults: false,
  selectedContact: null,
  delayDisplay: false,
  modalCreateContact: null,
  modalSearchContact: null,
  noSearch: true,
  init() {
    this.Modal = Modal(this);
  },
  onSearch() {
    this.delayDisplay = true;
    this.noSearch = false;
    this.selectedContact = null;
    if (this.userInput.length > 0 && this.selectedContact === null) {
      this.contactsFound = [];
      api.get(searchContactsUrl(this.userInput)).then((response) => {
        this.searchResults = response.data;
        this.contactsFound = this.searchResults.results;
        this.showContactsresults = this.contactsFound.length > 0;
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
    this.isModalCreateContactOpen = true;
  },
  closeModalCreateContact() {
    this.isModalCreateContactOpen = false;
    this.modalSearchContact.classList.toggle('d-none');
  },
}));
