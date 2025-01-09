import Alpine from 'alpinejs';
import api, { hitCountUrl } from '../utils/api';

function ContactAsk () {
  return {
    contactsIds:[], //tableau des contacts
    init() {
     this.contactsIds = JSON.parse(localStorage.getItem('contacts')) || [];
    },
    isLoaded(contactId) {
        for (let i = 0; i < this.contactsIds.length; i++) {
            if (this.contactsIds[i] === contactId) {
                return true;
            }
        }
        return false;
    },
    togglecliqueUser(contactId, resourceId) {
        this.contactsIds=[...this.contactsIds,contactId];

        api.post(hitCountUrl(), {
          'content_object_ct': 'addressbook.contact',
          'content_object_id': contactId,
          'context_object_ct': 'tasks.task',
          'context_object_id': resourceId
        });

        localStorage.setItem('contacts', JSON.stringify(this.contactsIds));
    },
  };
}

Alpine.data('ContactAsk', ContactAsk);
