import Alpine from 'alpinejs';
import api, { contactsUrl, contactUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('CreateContactModal', () => {
  return {
    Modal: null,
    isFormInEditMode: false,
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
        throw new Error('Error while creating a contact ', error);
      }
    },
    updateContact() {
      try {
        this.formState.fields = {
          isJobSelected: Boolean(this.contact.division),
          isMailOrPhone:
            this.contact.email.length !== 0 ||
            this.contact.phone_no.length !== 0,
          isFormatEmailValid: this.contact.email
            ? this.contact.email.match(/^[\w.\-]+@([\w\-]+\.)+[\w\-]{2,4}$/)
            : true,
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

          api.patch(contactUrl(this.contact.id), payload).then((response) => {
            this.Modal.closeModal();
            location.reload();
          });
        }
      } catch (error) {
        throw new Error('Error while updating a contact ', error);
      }
    },
    handleSetOrganization(organization) {
      this.contact.organization = organization;
      this.formState.fields.isOrgaSelected = true;
    },
    isCreateOrganizationModalOpen: false,
    openModalCreateOrganization() {
      // hide create contact modal
      this.modalCreateContact = this.$refs.createContactModal;
      this.modalCreateContact.classList.toggle('d-none');
      // create organization modal
      this.isCreateOrganizationModalOpen = true;
      this.$store.crisp.isPopupOpen = true;
    },
    closeCreateOrganizationModal(event) {
      if (event.target.id !== 'create-organization-modal') {
        return;
      }
      if (event.detail) {
        this.handleSetOrganization(event.detail);
      }
      this.isCreateOrganizationModalOpen = false;
      this.$store.crisp.isPopupOpen = false;
      this.modalCreateContact.classList.toggle('d-none');
    },
    initCreateContactModalData($event) {
      this.contact = { ...$event.detail };
      if (this.contact.id) {
        this.isFormInEditMode = true;
      }
      if (this.contact.organization) {
        this.formState.fields.isOrgaSelected = true;
      }
      // this.formState.fields.isJobSelected = Boolean(this.contact.division);
      // this.formState.fields.isMailOrPhone =
      //   this.contact.email.length !== 0 || this.contact.phone_no.length !== 0;
      // this.formState.fields.isFormatEmailValid = this.contact.email.match(
      //   /^[\w.\-]+@([\w\-]+\.)+[\w\-]{2,4}$/
      // );
    },
  };
});
