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
    init() {
    },
    onSearch() {
      this.delayDisplay = true;
      if (this.userInput.length > 0 && !this.isAContactSelected) {
        api.get(searchContactsUrl(this.userInput)).then((response) => {
          this.searchResults = response.data;
          this.contactsFound = this.searchResults.results;
            if(this.contactsFound.length > 0) {
              this.showContactsresults = true;
            }
            else {
              this.showContactsresults = false;
            }
          });
      }
    },
    onSelect(contact) {
      console.log('selected contact : ', contact);
      this.selectedContact = contact;
      this.isAContactSelected = true;
    },
    addContact() {
      let textArea = document.querySelector('.tiptap.ProseMirror');
      textArea.innerHTML += `<div class="fr-p-3v">
    <div class="d-flex">
        <div>
            <span class="same-for-all-text contact-names fr-pr-1v">${this.selectedContact.first_name}</span>
        </div>
        <div>
            <span class="same-for-all-text contact-names fr-pr-1v">${this.selectedContact.last_name}</span>
        </div>
        <div>
            <span class="color-3a3a3a text-position">role organisation</span>
        </div>
    </div>
    <div>
        <span class="color-3a3a3a text-organisation">Organisation</span>
    </div>
    <div>
        <a href="mailto:${this.selectedContact.email}"
           class="same-for-all-text text-position">${this.selectedContact.email}
        </a>
    </div>
    <div>
        <a href="tel:+0606060606" class="same-for-all-text text-position"><span class="fr-icon--sm fr-icon-phone-line" aria-hidden="true"></span> tel user</a>
    </div>
    <div>
        <a href="tel:+0606060606" class="same-for-all-text text-position"><span class="fr-icon--sm fr-icon-phone-line" aria-hidden="true"></span> num user</a>
    </div>
    <div>
        <span class="same-for-all-text text-date">mis à jour le xxxxxx</span>
    </div>
</div>`;
      this.closeModal();
    },
    closeModal() {
      this.isAContactSelected = false;
      this.showContactsresults = false
      this.userInput = '';
      this.isOpenModal = false;
    },
  };
}

Alpine.data('SearchContact', SearchContact);
