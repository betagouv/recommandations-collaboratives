import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';

function CreateContact() {
  return {
    modalCreateContact: null,
    modalSearchContact: null,
    contact: {
          organization: '',
          last_name: '',
          first_name: '',
          division: '',
          email: '',
          phone_no: '',
          mobile_no: '',
        },
    isOrgaSelected: false,
    isJobSelected: false,
    isMailOrPhone: false,
    init() {},
    closeCreateContactModal() {
      this.modalCreateContact = document.querySelector('#create-contact-modal');
      this.modalCreateContact.classList.toggle('d-none');
      this.isOrgaSelected = false;
      this.isJobSelected = false;
      this.isMailOrPhone = false;
      this.reOpenModalSearchContact();
    },
    reOpenModalSearchContact() {
      this.modalSearchContact = document.querySelector('#search-contact-modal');
      this.modalSearchContact.classList.toggle('d-none');
    },
    createContact() {
      if (this.$store.contact.orgaSelected) {
        const tempOrg = this.$store.contact.orgaSelected;
        this.contact.organization = tempOrg.id;
        this.isOrgaSelected = false;
      } else {
        this.isOrgaSelected = true;
      }
      if (this.contact.division.length === 0) {
        this.isJobSelected = true;
      } else {
        this.isJobSelected = false;
      }
      this.isMailOrPhone = this.contact.email.length === 0 && this.contact.phone_no.length === 0;
      if (
        this.contact.organization &&
        this.contact.division.length > 0 &&
        (this.contact.email.length > 0 || this.contact.phone_no.length > 0)
      ) {
        api.post(contactsUrl(), this.contact).then((response) => {
          this.$store.contact.createdContact = response.data;
          this.$dispatch('reset-orga', null);
          this.resetFormValue();
          this.closeCreateContactModal();
        });
      }
    },
    resetFormValue() {
      this.contact.last_name = '';
      this.contact.first_name = '';
      this.contact.division = '';
      this.contact.email = '';
      this.contact.phone_no = '';
      this.contact.mobile_no = '';
      this.contact.organization = '';
      this.$store.contact.orgaSelected = null;
      this.isMailOrPhone = false;
    },
  };
}

Alpine.data('CreateContact', CreateContact);
