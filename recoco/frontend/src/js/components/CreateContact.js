import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';

function CreateContact() {
  return {
    modalCreateContact : null,
    modalSearchContact : null,
    contact : null,
    contactOrganization: null,
    contactLastName: '',
    contactFirstName: '',
    contactJob: '',
    contactEmail: '',
    contactTel: '',
    contactPhone: '',
    init() {
    },
    closeCreateContactModal() {
        this.modalCreateContact = document.querySelector('#create-contact-modal');
        this.modalCreateContact.classList.toggle('d-none');
        this.reOpenModalSearchContact();
    },
    reOpenModalSearchContact() {
        this.modalSearchContact = document.querySelector('#search-contact-modal');
        this.modalSearchContact.classList.toggle('d-none');
    },
    createContact() {
      console.log('jkesako dans mon store : ', this.$store.contact.orgaSelected);
      if(this.$store.contact.orgaSelected) {
        alert('mon orga se passe bien');
        this.contactOrganization = this.$store.contact.orgaSelected;
        console.log('jkesako dans mon orga : ', this.contactOrganization);
      }
      if(this.contactOrganization && this.contactJob.length > 0 && (this.contactEmail.length > 0 || this.contactTel.length > 0)) {
        alert('createContact');
        this.contact = {
          "organization": this.contactOrganization.id,
          "last_name": this.contactLastName,
          "first_name": this.contactFirstName,
          "division": this.contactJob,
          "email": this.contactEmail,
          "tel": this.contactTel,
          "phone": this.contactPhone
        };
        api.post(contactsUrl(),this.contact);
      }
    }
  };
}

Alpine.data('CreateContact', CreateContact);
