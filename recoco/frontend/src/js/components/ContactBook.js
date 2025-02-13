import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';

Alpine.data('ContactBook', () => {
  return {
    search: '',
    contacts: [],
    letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
    async init() {
      try {
        const response = await api.get(contactsUrl(50));
        this.contacts = response.data.results;
      } catch (error) {
        throw new Error('Erreur lors de la récupération des contacts');
      }
    },
  };
});
