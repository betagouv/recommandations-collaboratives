import Alpine from 'alpinejs';
import api, { contactsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal';

Alpine.data('CreateContactModal', () => {
  return {
    Modal: null,
    contact: {
      organization: '',
      last_name: '',
      first_name: '',
      division: '',
      email: '',
      phone_no: '',
      mobile_no: '',
    },
    formState: {
      isSubmitted: false,
      isValid: false,
      fields: {
        isOrgaSelected: false,
        isJobSelected: false,
        isMailOrPhone: false,
        isFormatEmailValid: false,
      },
    },
    init() {
      this.Modal = Modal(this, 'create-contact-modal');
    },
    createContact() {
      this.formState.fields = {
        isOrgaSelected: this.contact.organization !== '',
        isJobSelected: Boolean(this.contact.division),
        isMailOrPhone:
          this.contact.email.length !== 0 || this.contact.phone_no.length !== 0,
        isFormatEmailValid: this.contact.email.match(
          /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/
        ),
      };

      this.formState.isSubmitted = true;
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
          this.$dispatch('reset-orga', null); // FIXME

          this.Modal.responseModal(response.data);
        });
      }
    },
    handleSetOrganization(organization) {
      this.contact.organization = organization;
    },
  };
});
