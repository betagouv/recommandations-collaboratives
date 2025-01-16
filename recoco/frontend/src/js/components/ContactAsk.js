import Alpine from 'alpinejs';
import api, { hitCountUrl } from '../utils/api';

function ContactAsk(isStaff, isAdmin, isAdvisor, contactsToDisplay = []) {
  return {
    contactsIds: contactsToDisplay, //tableau des contacts
    init() {
    },
    isLoaded(contactId) {
      return isStaff || isAdmin || isAdvisor || this.contactsIds.includes(contactId);
    },
    toggleUserClic(contactId, resourceId) {
      this.contactsIds = [...this.contactsIds, contactId];
      api.post(hitCountUrl(), {
        content_object_ct: 'addressbook.contact',
        content_object_id: contactId,
        context_object_ct: 'resources.resource',
        context_object_id: resourceId,
      });
    },
  };
}

Alpine.data('ContactAsk', ContactAsk);
