import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../utils/api';
import { use } from 'marked';

function CreateContact() {
  return {
    orgaFound: [],
    userInput: '',
    init() {
    },
    onSearch() {
      if (this.userInput.length > 0) {
        this.orgaFound = [];
        // api.get(searchContactsUrl(this.userInput)).then((response) => {
        //   this.searchResults = response.data;
        //   this.contactsFound = this.searchResults.results;
        //     if(this.contactsFound.length > 0) {
        //       this.showContactsresults = true;
        //     }
        //     else {
        //       this.showContactsresults = false;
        //     }
        //   });
      }
    },
    closeModal() {
      this.isAContactSelected = false;
      this.showContactsresults = false
      this.userInput = '';
      this.isOpenCreateContactModal = false;
    },
    onCancelSelectContact(){
      this.isAContactSelected=false;
       this.selectedContact = null;
    }
  };
}

Alpine.data('SearchContact', SearchContact);
