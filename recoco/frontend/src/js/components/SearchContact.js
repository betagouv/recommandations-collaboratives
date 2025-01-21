import Alpine from 'alpinejs';
import { Modal } from 'bootstrap';

function SearchContact() {
  return {
    searchResults: [],
    isOpenModal: false,
    userInput: '',
    init() {
     console.log('coucou');
    },
    onSearch() {
      // call api get users by text sur addressbook/contacts
      console.log('searching : ', this.userInput); // console log retour api
      // le mettre dans une variable résultat de recherche
    },
  };
}

Alpine.data('SearchContact', SearchContact);
