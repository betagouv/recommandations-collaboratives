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
    isOrgaSelected: true,
    isJobSelected: true,
    isMailOrPhone: false,
    init() {},
    closeModal(clearForm = false, reOpenSearchContact = false) {
      this.isOrgaSelected = true;
      this.isJobSelected = true;
      this.isMailOrPhone = false;

      if (clearForm) {
        this.resetFormValue();
      }
      if (reOpenSearchContact) {
        this.reOpenModalSearchContact();
      }
      else {
        this.$store.contact.openModal = '';
      }
    },
    reOpenModalSearchContact() {
      this.$store.contact.openModal = 'searchContact';
    },
    createContact() {
      this.isOrgaSelected = this.contact.organization == null;

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
          this.$dispatch('set-contact', response.data);
          this.$dispatch('reset-orga', null); // FIXME

          this.closeModal(true);
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
