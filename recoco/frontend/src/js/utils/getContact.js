import api, { contactUrl } from './api';

export default async function getContact(contactId) {
  return api
    .get(contactUrl(contactId))
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      console.error('Error fetching contact:', error);
    });
}
