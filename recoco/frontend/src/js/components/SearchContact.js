import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../utils/api';

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

      this.closeModal();
    },
    closeModal() {
      this.selectedContact = null;
      this.showContactsresults = false;
      this.userInput = '';
      this.noSearch = true;
      this.$store.contact.openModal = '';
    },
    onCancelSelectContact() {
      this.selectedContact = null;
    },
    openModalSearchContact() {
      this.$store.contact.openModal = 'searchContact';
    },
    openModalCreateContact() {
      this.$store.contact.openModal = 'createContact';
    },
  };
}

Alpine.data('SearchContact', SearchContact);
