import Alpine from 'alpinejs';
import api, { searchContactsUrl } from '../utils/api';

function SearchContact() {
  return {
    searchResults: [],
    contactsFound: [],
    isOpenModal: false,
    userInput: '',
    init() {
    },
    onSearch() {
      // call api get users by text sur addressbook/contacts
      if (this.userInput.length > 0) {
      api.get(searchContactsUrl(this.userInput)).then((response) => {
        this.searchResults = response.data;
        this.contactsFound = this.searchResults.results;
          this.$refs.test.ariaExpanded = 'true';
          console.log('searching : ', this.searchResults); // console log retour api
          console.log('searching : ', this.contactsFound); // console log retour api
        });
      }

      console.log("is expend : ",this.$refs.test.ariaExpanded);

    },
  };
}

Alpine.data('SearchContact', SearchContact);
