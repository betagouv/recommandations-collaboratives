import Alpine from 'alpinejs';
import api, { hitCountUrl } from '../utils/api';

function ContactAsk(canSeeEverything, contactsToDisplay = []) {
  return {
    contactsIds: [],
    canSeeEverything: false,
    init() {
      this.contactsIds = contactsToDisplay;
      this.canSeeEverything = canSeeEverything;
    },
    isLoaded(contactId) {
      return this.canSeeEverything || this.contactsIds.includes(contactId);
    },
    toggleUserClic(contactId, contextObjectID, contextObjectCT) {
      this.contactsIds = [...this.contactsIds, contactId];
      api.post(hitCountUrl(), {
        content_object_ct: 'addressbook.contact',
        content_object_id: contactId,
        context_object_ct: contextObjectCT,
        context_object_id: contextObjectID,
      });
    },
  };
}

Alpine.data('ContactAsk', ContactAsk);
