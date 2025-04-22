import Alpine from 'alpinejs';
import api, { contactUrl } from '../../utils/api.js';
import { formatDate } from '../../utils/date';

Alpine.data('GetContactObject', (contactId) => ({
  contact: null,
  formatDate,
  init() {
    api
      .get(contactUrl(contactId))
      .then((response) => {
        this.contact = response.data;
      })
      .catch((error) => {
        console.error('Error fetching contact:', error);
      });
  },
}));
