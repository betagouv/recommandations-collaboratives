import Alpine from 'alpinejs';
import api, { searchOrganizationGroupsUrl } from '../utils/api';

function CreateOrganisation() {
  return {
    verifNomOrga: false,
    organisationName: '',
    isGroupNat: false,
    organisationGroup: '',
    orgaGroupsFound: [],
    userInput: '',
    showOrgaGroupsresults: false,
    isAnOrgaGroupSelected: false,
    init() {},
    closeCreateOrganisationModal() {
      this.modalCreateOrganisation = document.querySelector('#create-organisation-modal');
      this.modalCreateOrganisation.classList.toggle('d-none');
      this.reOpenModalCreateContact();
    },
    reOpenModalCreateContact() {
      this.modalSearchOrganisation = document.querySelector('#create-contact-modal');
      this.modalSearchOrganisation.classList.toggle('d-none');
    },
    createOrganisation() {

    },
    setGroupNatToTrue() {
      this.isGroupNat = true;
    },
    setGroupNatToFalse() {
      this.isGroupNat = false;
    },
    onSearchOrgaGroup() {
      this.isAnOrgaSelected = false;
      if (this.userInput.length > 0) {
        this.orgaGroupFound = [];
        api.get(searchOrganizationGroupsUrl(this.userInput)).then((response) => {
          this.searchResults = response.data;
          this.orgaGroupsFound = this.searchResults.results;
          if (this.orgaGroupsFound.length > 0) {
            this.showOrgaGroupsresults = true;
          } else {
            this.showOrgaGroupsresults = false;
          }
        });
      }
    },
    // createContact() {
    //   if (this.$store.contact.orgaSelected) {
    //     this.contactOrganization = this.$store.contact.orgaSelected;
    //     this.verifOrga = false;
    //   } else {
    //     this.verifOrga = true;
    //   }
    //   if (this.contactJob.length === 0) {
    //     this.verifPoste = true;
    //   } else {
    //     this.verifPoste = false;
    //   }
    //   if (this.contactEmail.length === 0 || this.contactTel.length === 0) {
    //     this.verifMailOrPhone = true;
    //   } else {
    //     this.verifMailOrPhone = false;
    //   }
    //   if (
    //     this.contactOrganization &&
    //     this.contactJob.length > 0 &&
    //     (this.contactEmail.length > 0 || this.contactTel.length > 0)
    //   ) {
    //     this.contact = {
    //       organization: this.contactOrganization.id,
    //       last_name: this.contactLastName,
    //       first_name: this.contactFirstName,
    //       division: this.contactJob,
    //       email: this.contactEmail,
    //       phone_no: this.contactTel,
    //       mobile_no: this.contactPhone,
    //     };
    //     api.post(contactsUrl(), this.contact).then((response) => {
    //       this.contact = response.data;
    //       this.$store.contact.createdContact = this.contact;
    //     });
    //     this.resetFormValue();
    //     this.closeCreateContactModal();
    //   }
    // },
    resetFormValue() {
    },
  };
}

Alpine.data('CreateOrganisation', CreateOrganisation);
