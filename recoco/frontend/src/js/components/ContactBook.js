import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';

Alpine.data('ContactBook', () => {
  return {
    search: '',
    contacts: [],
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    contactListGroupByOrganization: {},
    async init() {
      try {
        const response = await api.get(contactsUrl(500));
        // Help me with this line
        this.contactListGroupByOrganization = Object.groupBy(
          response.data.results,
          ({ organization: { name } }) => name
        );
        console.log(this.contactListGroupByOrganization);

        this.contacts = response.data.results;
      } catch (error) {
        // TODO add a toast
        console.error(error);
        throw new Error('Erreur lors de la récupération des contacts');
      }
    },
    loadOrganizationStartingWith(letter) {},
  };
});
