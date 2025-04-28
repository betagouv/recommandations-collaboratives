import Alpine from 'alpinejs';
import api, { searchOrganizationGroupsUrl, departmentsUrl, organizationsUrl, organizationGroupsUrl } from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('CreateOrganizationModal', () => {
  return {
    Modal: null,
    orgaGroupsFound: [],
    userInput: '',
    showOrgaGroupsresults: false,
    isAnOrgaGroupSelected: false,
    departments: [],
    organization: {
      name: '',
      group: null,
      departments: [],
    },
    formState: {
      isSubmitted: false,
      fields: {
        isOrgaName: false,
        isGroupNat: false,
        isGroupNatName: false,
      },
    },
    async init() {
      this.Modal = Modal(this, 'create-organization-modal');
      await this.showDepartments();
    },
    setGroupNatToFalse() {
      this.formState.fields.isGroupNat = false;
      this.userInput = '';
      this.organization.group = null;
    },
    onSearchOrgaGroup() {
      this.isAnOrgaSelected = false;
      try {
        if (this.userInput.length > 0) {
          this.organization.group = null;
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
      this.organization.group = group.id;
      this.userInput = group.name;
      this.showOrgaGroupsresults = false;
    },
    createOrganizationGroup() {

      this.organization.group = {
        name: this.userInput,
      };
      this.isAnOrgaGroupSelected = true;
      this.showOrgaGroupsresults = false;
      try {
            api.post(organizationGroupsUrl(), this.organization.group).then((response) => {
                this.organization.group = response.data.id;
            });
          } catch (error) {
            console.log(error);
          }
    },
    createOrganization() {
      this.formState.fields = {
        isOrgaName: this.organization.name !== '',
        isGroupNat: this.formState.fields.isGroupNat == 'true',
        isGroupNatName: this.organization.group !== null && this.formState.fields.isGroupNat,
      };
      this.formState.isSubmitted = true;

      if(this.formState.fields.isGroupNatName && this.formState.fields.isOrgaName || !this.formState.fields.isGroupNat && this.formState.fields.isOrgaName) {
        api.post(organizationsUrl(), this.organization).then((response) => {
            this.Modal.responseModal(response.data);
        }).catch ((error) =>{
          console.log(error);
        });
      }
    },
    handleDepartmentsSelection(departments) {
      this.organization.departments = departments;
    }
  };
})
