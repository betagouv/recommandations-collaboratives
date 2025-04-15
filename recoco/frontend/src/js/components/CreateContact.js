import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';

function CreateContact() {
  return {
    modalCreateContact: null,
    modalSearchContact: null,
    contact: null,
    contactOrganization: null,
    contactLastName: '',
    contactFirstName: '',
    contactJob: '',
    contactEmail: '',
    contactTel: '',
    contactPhone: '',
    verifOrga: false,
    verifPoste: false,
    verifMailOrPhone: false,
    init() {},
    closeCreateContactModal() {
      this.modalCreateContact = document.querySelector('#create-contact-modal');
      this.modalCreateContact.classList.toggle('d-none');
      this.reOpenModalSearchContact();
    },
    reOpenModalSearchContact() {
      this.modalSearchContact = document.querySelector('#search-contact-modal');
      this.modalSearchContact.classList.toggle('d-none');
    },
    openCreateOrganizationModal() {
      this.modalCreateOrganization = document.querySelector('#create-organization-modal');
      this.modalCreateOrganization.classList.toggle('d-none');
      this.modalCreateContact = document.querySelector('#create-contact-modal');
      this.modalCreateContact.classList.toggle('d-none');
    },
    createContact() {
      try {
        if (this.$store.contact.orgaSelected) {
          this.contactOrganization = this.$store.contact.orgaSelected;
          this.verifOrga = false;
        } else {
          this.verifOrga = true;
        }
        if (this.contactJob.length === 0) {
          this.verifPoste = true;
        } else {
          this.verifPoste = false;
        }
        if (this.contactEmail.length === 0 || this.contactTel.length === 0) {
          this.verifMailOrPhone = true;
        } else {
          this.verifMailOrPhone = false;
        }
        if (
          this.contactOrganization &&
          this.contactJob.length > 0 &&
          (this.contactEmail.length > 0 || this.contactTel.length > 0)
        ) {
          this.contact = {
            organization: this.contactOrganization.id,
            last_name: this.contactLastName,
            first_name: this.contactFirstName,
            division: this.contactJob,
            email: this.contactEmail,
            phone_no: this.contactTel,
            mobile_no: this.contactPhone,
          };
          api.post(contactsUrl(), this.contact).then((response) => {
            this.contact = response.data;
            this.$store.contact.createdContact = this.contact;
            console.log('createdContact', this.$store.contact.createdContact);
          });
          this.resetFormValue();
          this.closeCreateContactModal();
        }
      } catch (error) {
        console.log(error);
         throw new Error('Error while creating a contact ', error);
      }
    },
    resetFormValue() {
      this.contactLastName = '';
      this.contactFirstName = '';
      this.contactJob = '';
      this.contactEmail = '';
      this.contactTel = '';
      this.contactPhone = '';
      this.verifMailOrPhone = false;
      this.contactOrganization = null;
      this.$store.contact.orgaSelected = null;
      this.$store.contact.orgaCreated = null;
      this.$dispatch('reset-orga-name');
    },
  };
}

Alpine.data('CreateContact', CreateContact);
