import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../utils/api';

// TODO Modal controller search contact
function SearchContact() {
  return {
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
    init() {},
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
      this.$dispatch('set-contact', this.selectedContact);
    },
    onCancelSelectContact() {
      this.selectedContact = null;
    },
    openModalCreateContact() {
      this.modalCreateContact = this.$refs.createContactModal;
      this.modalCreateContact.classList.toggle('d-none');
      // TODO hide search contact modal
      // this.closeModal();
    },
  };
}

Alpine.data('SearchContact', SearchContact);
