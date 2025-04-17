import Alpine from 'alpinejs';
import api, { contactsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('CreateContactModal', () => {
  return {
    Modal: null,
    contact: {
      organization: {name: ''},
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
    createContact() {
      this.formState.fields = {
        isOrgaSelected: this.contact.organization !== '',
        isJobSelected: Boolean(this.contact.division),
        isMailOrPhone:
          this.contact.email.length !== 0 || this.contact.phone_no.length !== 0,
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
          this.Modal.responseModal({... this.contact, id : response.data.id});
        });
      }
    },
    handleSetOrganization(organization) {
      this.contact.organization = organization;
      console.log('contact.organization', this.contact.organization);
    },
    // TODO : voir si on peut mettre ce code dans un "meilleur endroit"
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
        console.log("coucou");
        this.$refs.orgSearch.resetSearchResultDisplayWhenOrgaCreated(false);
      }
      this.isCreateOrganizationModalOpen = false;
      this.modalCreateContact.classList.toggle('d-none');
    },
  };
});


// import Alpine from 'alpinejs';
// import api, { contactsUrl } from '../utils/api';

// function CreateContact() {
//   return {
//     modalCreateContact: null,
//     modalSearchContact: null,
//     contact: null,
//     contactOrganization: null,
//     contactLastName: '',
//     contactFirstName: '',
//     contactJob: '',
//     contactEmail: '',
//     contactTel: '',
//     contactPhone: '',
//     verifOrga: false,
//     verifPoste: false,
//     verifMailOrPhone: false,
//     init() {},
//     closeCreateContactModal() {
//       this.modalCreateContact = document.querySelector('#create-contact-modal');
//       this.modalCreateContact.classList.toggle('d-none');
//       this.reOpenModalSearchContact();
//     },
//     reOpenModalSearchContact() {
//       this.modalSearchContact = document.querySelector('#search-contact-modal');
//       this.modalSearchContact.classList.toggle('d-none');
//     },
//     openCreateOrganisationModal() {
//       this.modalCreateOrganisation = document.querySelector('#create-organisation-modal');
//       this.modalCreateOrganisation.classList.toggle('d-none');
//       this.modalCreateContact = document.querySelector('#create-contact-modal');
//       this.modalCreateContact.classList.toggle('d-none');
//     },
//     createContact() {
//       try {
//         if (this.$store.contact.orgaSelected) {
//           this.contactOrganization = this.$store.contact.orgaSelected;
//           this.verifOrga = false;
//         } else {
//           this.verifOrga = true;
//         }
//         if (this.contactJob.length === 0) {
//           this.verifPoste = true;
//         } else {
//           this.verifPoste = false;
//         }
//         if (this.contactEmail.length === 0 || this.contactTel.length === 0) {
//           this.verifMailOrPhone = true;
//         } else {
//           this.verifMailOrPhone = false;
//         }
//         if (
//           this.contactOrganization &&
//           this.contactJob.length > 0 &&
//           (this.contactEmail.length > 0 || this.contactTel.length > 0)
//         ) {
//           this.contact = {
//             organization: this.contactOrganization.id,
//             last_name: this.contactLastName,
//             first_name: this.contactFirstName,
//             division: this.contactJob,
//             email: this.contactEmail,
//             phone_no: this.contactTel,
//             mobile_no: this.contactPhone,
//           };
//           api.post(contactsUrl(), this.contact).then((response) => {
//             this.contact = response.data;
//             this.$store.contact.createdContact = this.contact;
//             console.log('createdContact', this.$store.contact.createdContact);
//           });
//           this.resetFormValue();
//           this.closeCreateContactModal();
//         }
//       } catch (error) {
//         console.log(error);
//          throw new Error('Error while creating a contact ', error);
//       }
//     },
//     resetFormValue() {
//       this.contactLastName = '';
//       this.contactFirstName = '';
//       this.contactJob = '';
//       this.contactEmail = '';
//       this.contactTel = '';
//       this.contactPhone = '';
//       this.verifMailOrPhone = false;
//       this.contactOrganization = null;
//       this.$store.contact.orgaSelected = null;
//       this.$store.contact.orgaCreated = null;
//       this.$dispatch('reset-orga-name');
//     },
//   };
// }

// Alpine.data('CreateContact', CreateContact);
