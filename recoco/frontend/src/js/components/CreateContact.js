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
    isOrgaSelected: false,
    isJobSelected: false,
    isMailOrPhone: false,
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
    createContact() {
      if (this.$store.contact.orgaSelected) {
        this.contactOrganization = this.$store.contact.orgaSelected;
        this.isOrgaSelected = false;
      } else {
        this.isOrgaSelected = true;
      }
      if (this.contactJob.length === 0) {
        this.isJobSelected = true;
      } else {
        this.isJobSelected = false;
      }
      this.isMailOrPhone = this.contactEmail.length === 0 || this.contactTel.length === 0;
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
        });
        this.resetFormValue();
        this.closeCreateContactModal();
      }
    },
    resetFormValue() {
      this.contactLastName = '';
      this.contactFirstName = '';
      this.contactJob = '';
      this.contactEmail = '';
      this.contactTel = '';
      this.contactPhone = '';
      this.contactOrganization = null;
      this.$store.contact.orgaSelected = null;
      this.isMailOrPhone = false;
      // this.$store.contact.createdContact = null;
    },
  };
}

Alpine.data('CreateContact', CreateContact);
