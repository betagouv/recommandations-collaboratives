import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../utils/api';

function SearchContact() {
  return {
    searchResults: [],
    contactsFound: [],
    isOpenModal: false,
    userInput: '',
    showContactsresults: false,
    isAContactSelected: false,
    selectedContact: null,
    delayDisplay: false,
    modalCreateContact: null,
    modalSearchContact: null,
    noSearch: true,
    init() {},
    onSearch() {
      this.delayDisplay = true;
      this.noSearch = false;
      if (this.userInput.length > 0 && !this.isAContactSelected) {
        this.contactsFound = [];
        try {
          api.get(searchContactsUrl(this.userInput)).then((response) => {
            this.searchResults = response.data;
            this.contactsFound = this.searchResults.results;
            if (this.contactsFound.length > 0) {
              this.showContactsresults = true;
            } else {
              this.showContactsresults = false;
            }
          });
        } catch (error) {
          console.log(error);
        }
      } else if (this.userInput.length === 0) {
        this.noSearch = true;
      }
    },
    onSelect(contact) {
      this.noSearch = false;
      this.selectedContact = contact;
      this.isAContactSelected = true;
    },
    addContact() {
      let textArea = document.querySelector('.tiptap.ProseMirror');
      textArea.innerHTML += `@ ${this.selectedContact.first_name} ${this.selectedContact.last_name}`;
      this.$store.previewModal.contact = this.selectedContact;
      this.noSearch = true;
      this.closeModal();
    },
    closeModal() {
      this.isAContactSelected = false;
      this.showContactsresults = false;
      this.userInput = '';
      this.modalSearchContact.classList.toggle('d-none');
    },
    onCancelSelectContact() {
      this.isAContactSelected = false;
      this.selectedContact = null;
    },
    openModalSearchContact() {
      this.modalSearchContact = document.querySelector('#search-contact-modal');
      this.modalSearchContact.classList.toggle('d-none');
    },
    openModalCreateContact() {
      this.modalCreateContact = document.querySelector('#create-contact-modal');
      this.modalCreateContact.classList.toggle('d-none');
      this.closeModalWithData();
    },
    closeModalWithData() {
      this.modalSearchContact = document.querySelector('#search-contact-modal');
      this.modalSearchContact.classList.toggle('d-none');
    },
  };
}

Alpine.data('SearchContact', SearchContact);
