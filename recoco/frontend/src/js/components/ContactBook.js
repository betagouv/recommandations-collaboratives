import Alpine from 'alpinejs';
import api, { contactsUrl, searchContactsUrl } from '../utils/api';

Alpine.data('ContactBook', () => {
  return {
    searchParams: {
      search: '',
      letter: null,
    },
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    contactListGroupByOrganization: {},
    async init() {
      try {
        const response = await api.get(contactsUrl(25));
        this.contactListGroupByOrganization = this.groupContactByOrganization(
          response.data.results
        );
      } catch (error) {
        // TODO add a toast
        console.error(error);
        throw new Error('Erreur lors de la récupération des contacts');
      }
    },
    searchContacts(search) {
      this.searchParams.search = search;
      this.getContactData();
    },
    loadOrganizationStartingWith(letter) {
      if (letter === this.searchParams.letter) {
        return;
      }
      this.searchParams.letter = letter;
      this.getContactData();
    },
    async getContactData() {
      const response = await api.get(
        searchContactsUrl(this.searchParams.search, this.searchParams.letter)
      );
      this.contactListGroupByOrganization = this.groupContactByOrganization(
        response.data.results
      );
    },
    groupContactByOrganization(contactList) {
      return Object.groupBy(contactList, ({ organization: { name } }) => name);
    },
  };
});
