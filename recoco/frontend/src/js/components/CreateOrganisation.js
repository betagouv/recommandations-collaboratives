import Alpine from 'alpinejs';
import api, { searchOrganizationGroupsUrl, departmentsUrl, organizationsUrl, organizationGroupsUrl } from '../utils/api';

function CreateOrganisation() {
  return {
    verifNomOrga: false,
    organisationName: '',
    isGroupNat: false,
    organisationGroup: null,
    orgaGroupsFound: [],
    userInput: '',
    showOrgaGroupsresults: false,
    isAnOrgaGroupSelected: false,
    departments: [],
    selectedDepartments: [],
    organisationToCreate: null,
    orgaToCreateFormIsOk: false,
    async init() {
       await this.showDepartments();
    },
    closeCreateOrganisationModal() {
      this.modalCreateOrganisation = document.querySelector('#create-organisation-modal');
      this.modalCreateOrganisation.classList.toggle('d-none');
      this.reOpenModalCreateContact();
    },
    reOpenModalCreateContact() {
      this.modalSearchOrganisation = document.querySelector('#create-contact-modal');
      this.modalSearchOrganisation.classList.toggle('d-none');
    },
    setGroupNatToTrue() {
      this.isGroupNat = true;
    },
    setGroupNatToFalse() {
      this.isGroupNat = false;
      this.userInput = '';
      this.organisationGroup = null;
    },
    onSearchOrgaGroup() {
      this.isAnOrgaSelected = false;
      try {
        if (this.userInput.length > 0) {
          this.organisationGroup = null;
          this.showOrgaGroupsresults = true
          this.isAnOrgaGroupSelected = false;
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
      } catch (error) {
        console.log(error);
         throw new Error('Error while fetching organizations ', error);
      }
    },
    async showDepartments() {
      try {
        const response = await api.get(departmentsUrl());
        this.departments = response.data;
        this.$dispatch('on-department-fetch', this.departments);
      }
      catch (error) {
        console.log(error);
         throw new Error('Error while fetching departments ', error);
      }

    },
    onSelectGroup(group) {
      this.isAnOrgaGroupSelected = true;
      this.organisationGroup = group;
      this.userInput = group.name;
      this.showOrgaGroupsresults = false;
    },
    createOrganisationGroup() {
      this.organisationGroup = {
        name: this.userInput,
      };
      this.isAnOrgaGroupSelected = true;
      this.showOrgaGroupsresults = false;
      try {
            api.post(organizationGroupsUrl(), this.organisationGroup).then((response) => {
                this.organisationGroup = response.data;
            });
          } catch (error) {
            console.log(error);
          }
    },
    createOrganisation() {
        this.selectedDepartments = [...this.$store.contact.selectedDepartments];

        if(this.isGroupNat && this.organisationGroup === null){
          alert('Veuillez selectionner un groupe');
          this.orgaToCreateFormIsOk = false;
        }

        if (this.organisationName.length === 0) {
          this.verifNomOrga = true;
        }
        else {
          this.verifNomOrga = false;
          if (this.organisationGroup === null && this.selectedDepartments.length === 0) {
            this.organisationToCreate = {
                name: this.organisationName,
              };
          }
          else if (this.organisationGroup !== null && this.selectedDepartments.length === 0) {
            this.organisationToCreate = {
                name: this.organisationName,
                group: this.organisationGroup.id,
              };
          }
          else if (this.organisationGroup === null && this.selectedDepartments.length > 0) {
            this.organisationToCreate = {
                name: this.organisationName,
                departments: this.selectedDepartments,
              };
          }
          else {
              this.organisationToCreate = {
                name: this.organisationName,
                group: this.organisationGroup.id,
                departments: this.selectedDepartments,
              };
          }
          try {
            api.post(organizationsUrl(), this.organisationToCreate).then((response) => {
                this.organisationToCreate = response.data;
                this.$store.contact.orgaSelected = this.organisationToCreate;
                this.$store.contact.orgaCreated = this.organisationToCreate;
                this.resetFormValue();
                this.closeCreateOrganisationModal();
            });
          } catch (error) {
            console.log(error);
          }
        }
    },
    resetFormValue() {
      this.organisationName = '';
      this.organisationGroup = null;
      this.verifNomOrga = false;
      this.isGroupNat = false;
      this.isAnOrgaGroupSelected = false;
      this.userInput = '';
      this.showOrgaGroupsresults = false;
      this.selectedDepartments = [];
      const radioButton = document.querySelector('input[name="natGroup"]');
      radioButton.checked = false;
      this.$dispatch('reset-form-create-orga');
    },
  };
}

Alpine.data('CreateOrganisation', CreateOrganisation);
