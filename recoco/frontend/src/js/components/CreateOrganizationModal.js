import Alpine from 'alpinejs';
import api, { searchOrganizationGroupsUrl, departmentsUrl, organizationsUrl, organizationGroupsUrl } from '../utils/api';

Alpine.data('CreateOrganizationModal', () => {
  return {
    verifNomOrga: false,
    organizationName: '',
    isGroupNat: false,
    organizationGroup: null,
    orgaGroupsFound: [],
    userInput: '',
    showOrgaGroupsresults: false,
    isAnOrgaGroupSelected: false,
    departments: [],
    selectedDepartments: [],
    organizationToCreate: null,
    orgaToCreateFormIsOk: false,
    async init() {
       await this.showDepartments();
    },
    closeCreateOrganizationModal() {
      this.modalCreateOrganization = document.querySelector('#create-organization-modal');
      this.modalCreateOrganization.classList.toggle('d-none');
      this.reOpenModalCreateContact();
    },
    reOpenModalCreateContact() {
      this.modalSearchOrganization = document.querySelector('#create-contact-modal');
      this.modalSearchOrganization.classList.toggle('d-none');
    },
    setGroupNatToTrue() {
      this.isGroupNat = true;
    },
    setGroupNatToFalse() {
      this.isGroupNat = false;
      this.userInput = '';
      this.organizationGroup = null;
    },
    onSearchOrgaGroup() {
      this.isAnOrgaSelected = false;
      try {
        if (this.userInput.length > 0) {
          this.organizationGroup = null;
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
      this.organizationGroup = group;
      this.userInput = group.name;
      this.showOrgaGroupsresults = false;
    },
    createOrganizationGroup() {
      this.organizationGroup = {
        name: this.userInput,
      };
      this.isAnOrgaGroupSelected = true;
      this.showOrgaGroupsresults = false;
      try {
            api.post(organizationGroupsUrl(), this.organizationGroup).then((response) => {
                this.organizationGroup = response.data;
            });
          } catch (error) {
            console.log(error);
          }
    },
    createOrganization() {
        this.selectedDepartments = [...this.$store.contact.selectedDepartments];

        if(this.isGroupNat && this.organizationGroup === null){
          alert('Veuillez selectionner un groupe');
          this.orgaToCreateFormIsOk = false;
        }

        if (this.organizationName.length === 0) {
          this.verifNomOrga = true;
        }
        else {
          this.verifNomOrga = false;
          if (this.organizationGroup === null && this.selectedDepartments.length === 0) {
            this.organizationToCreate = {
                name: this.organizationName,
              };
          }
          else if (this.organizationGroup !== null && this.selectedDepartments.length === 0) {
            this.organizationToCreate = {
                name: this.organizationName,
                group: this.organizationGroup.id,
              };
          }
          else if (this.organizationGroup === null && this.selectedDepartments.length > 0) {
            this.organizationToCreate = {
                name: this.organizationName,
                departments: this.selectedDepartments,
              };
          }
          else {
              this.organizationToCreate = {
                name: this.organizationName,
                group: this.organizationGroup.id,
                departments: this.selectedDepartments,
              };
          }
          try {
            api.post(organizationsUrl(), this.organizationToCreate).then((response) => {
                this.organizationToCreate = response.data;
                this.$store.contact.orgaSelected = this.organizationToCreate;
                this.$store.contact.orgaCreated = this.organizationToCreate;
                this.resetFormValue();
                this.closeCreateOrganizationModal();
            });
          } catch (error) {
            console.log(error);
          }
        }
    },
    resetFormValue() {
      this.organizationName = '';
      this.organizationGroup = null;
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
})
