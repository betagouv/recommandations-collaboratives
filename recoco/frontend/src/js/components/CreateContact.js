import Alpine from 'alpinejs';
import api, { contactsUrl } from '../utils/api';
import { Modal } from '../models/Modal';

function CreateContact() {
  return {
    Modal: null,
    modalCreateContact: null,
    // modalSearchContact: null,
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
    init() {
      this.Modal = Modal(this, 'create-contact-modal');
    },
    closeModal() {
      this.modalCreateContact = this.$refs.createContactModal;

      // this.modalCreateContact.classList.toggle('d-none');
      this.isOrgaSelected = true;
      this.isJobSelected = true;
      this.isMailOrPhone = false;
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
    // resetFormValue() {
    //   this.contact.last_name = '';
    //   this.contact.first_name = '';
    //   this.contact.division = '';
    //   this.contact.email = '';
    //   this.contact.phone_no = '';
    //   this.contact.mobile_no = '';
    //   this.contact.organization = '';
    //   this.$store.contact.orgaSelected = null;
    //   this.isMailOrPhone = false;
    // },

    handleSetOrganization(organization) {
      this.contact.organization = organization;
    },
  };
}

Alpine.data('CreateContact', CreateContact);
