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
    closeModal(clearForm = false) {
      // this.modalCreateContact = document.querySelector('#create-contact-modal');
      // this.modalCreateContact.classList.toggle('d-none');
      this.isOrgaSelected = false;
      this.isJobSelected = false;
      this.isMailOrPhone = false;

      if (clearForm) {
        this.resetFormValue();
      }

      this.reOpenModalSearchContact();
    },
    reOpenModalSearchContact() {
      openModal = 'searchContact';
      // this.modalSearchContact = document.querySelector('#search-contact-modal');
      // this.modalSearchContact.classList.toggle('d-none');
    },
    createContact() {
      this.isOrgaSelected = this.contact.organization != null;

      this.isJobSelected = Boolean(this.contact.division);

      this.isMailOrPhone =
        this.contact.email.length === 0 && this.contact.phone_no.length === 0;
      if (
        this.contact.organization &&
        this.contact.division.length > 0 &&
        (this.contact.email.length > 0 || this.contact.phone_no.length > 0)
      ) {
        let payload = {
          ...this.contact,
          organization: this.contact.organization.id,
        };

        api.post(contactsUrl(), payload).then((response) => {
          this.$dispatch('set-contact', this.contact);
          this.$dispatch('reset-orga', null); // FIXME

          this.closeModal((clearForm = true));
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

    handleSetOrganization(organization) {
      this.contact.organization = organization;
    },
  };
}

Alpine.data('CreateContact', CreateContact);
