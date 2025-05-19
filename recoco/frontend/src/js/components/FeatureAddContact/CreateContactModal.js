import Alpine from 'alpinejs';
import api, { contactsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('CreateContactModal', () => {
  return {
    Modal: null,
    contact: {
      organization: { name: '' },
      last_name: '',
      first_name: '',
      division: '',
      email: '',
      phone_no: '',
      mobile_no: '',
    },
    formState: {
      isSubmitted: false,
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
    createContact(isItReturningData = false) {
      try {
        this.formState.fields = {
          isOrgaSelected: this.contact.organization !== '',
          isJobSelected: Boolean(this.contact.division),
          isMailOrPhone:
            this.contact.email.length !== 0 ||
            this.contact.phone_no.length !== 0,
          isFormatEmailValid: this.contact.email.match(
            /^[\w.\-]+@([\w\-]+\.)+[\w\-]{2,4}$/
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
            if (isItReturningData) {
              this.Modal.responseModal({
                ...this.contact,
                id: response.data.id,
              });
            } else {
              this.Modal.closeModal();
            }
          });
        }
      } catch (error) {
        console.log(error);
        throw new Error('Error while creating a contact ', error);
      }
    },
    handleSetOrganization(organization) {
      this.contact.organization = organization;
    },
    isCreateOrganizationModalOpen: false,
    openModalCreateOrganization() {
      // hide create contact modal
      this.modalCreateContact = this.$refs.createContactModal;
      this.modalCreateContact.classList.toggle('d-none');
      // create organization modal
      this.isCreateOrganizationModalOpen = true;
    },
    closeCreateOrganizationModal(event) {
      if (event.target.id !== 'create-organization-modal') {
        return;
      }
      if (event.detail) {
        this.handleSetOrganization(event.detail);
        this.formState.fields.isOrgaSelected = true;
      }
      this.isCreateOrganizationModalOpen = false;
      this.modalCreateContact.classList.toggle('d-none');
    },
  };
});
