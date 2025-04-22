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
      api.get(searchContactsUrl(this.userInputSearchContact)).then((response) => {
        const searchResults = response.data;
        this.contactsFound = searchResults.results;
      });
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


// import Alpine from 'alpinejs';
// import api, { searchContactsUrl } from '../utils/api';

// function SearchContact() {
//   return {
//     searchResults: [],
//     contactsFound: [],
//     isOpenModal: false,
//     userInputSearchContact: '',
//     showContactsresults: false,
//     isAContactSelected: false,
//     selectedContact: null,
//     delayDisplay: false,
//     modalCreateContact: null,
//     modalSearchContact: null,
//     noSearch: true,
//     init() {},
//     onSearch() {
//       this.delayDisplay = true;
//       this.noSearch = false;
//       if (this.userInputSearchContact.length > 0 && !this.isAContactSelected) {
//         this.contactsFound = [];
//         try {
//           api.get(searchContactsUrl(this.userInputSearchContact)).then((response) => {
//             this.searchResults = response.data;
//             this.contactsFound = this.searchResults.results;
//             if (this.contactsFound.length > 0) {
//               this.showContactsresults = true;
//             } else {
//               this.showContactsresults = false;
//             }
//           });
//         } catch (error) {
//           console.log(error);
//         }
//       } else if (this.userInputSearchContact.length === 0) {
//         this.noSearch = true;
//       }
//     },
//     onSelect(contact) {
//       this.noSearch = false;
//       this.selectedContact = contact;
//       this.isAContactSelected = true;
//     },
//     addContact() {
//       let textArea = document.querySelector('.tiptap.ProseMirror');
//       textArea.innerHTML += `@ ${this.selectedContact.first_name} ${this.selectedContact.last_name}`;
//       this.$store.previewModal.contact = this.selectedContact;
//       this.noSearch = true;
//       this.closeModal();
//     },
//     closeModal() {
//       this.isAContactSelected = false;
//       this.showContactsresults = false;
//       this.userInputSearchContact = '';
//       this.modalSearchContact.classList.toggle('d-none');
//     },
//     onCancelSelectContact() {
//       this.isAContactSelected = false;
//       this.selectedContact = null;
//     },
//     openModalSearchContact() {
//       this.modalSearchContact = document.querySelector('#search-contact-modal');
//       this.modalSearchContact.classList.toggle('d-none');
//     },
//     openModalCreateContact() {
//       this.modalCreateContact = document.querySelector('#create-contact-modal');
//       this.modalCreateContact.classList.toggle('d-none');
//       this.closeModalWithData();
//     },
//     closeModalWithData() {
//       this.modalSearchContact = document.querySelector('#search-contact-modal');
//       this.modalSearchContact.classList.toggle('d-none');
//     },
//   };
// }

// Alpine.data('SearchContact', SearchContact);
