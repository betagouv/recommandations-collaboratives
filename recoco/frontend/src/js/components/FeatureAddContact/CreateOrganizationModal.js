import Alpine from 'alpinejs';
import api, {
  searchOrganizationGroupsUrl,
  departmentsUrl,
  organizationsUrl,
  organizationGroupsUrl,
  getOrganizationById,
} from '../../utils/api';
import { Modal } from '../../models/Modal.model';

Alpine.data('CreateOrganizationModal', (data = null) => {
  return {
    Modal: null,
    orgaGroupsFound: [],
    userInput: '',
    showOrgaGroupsresults: false,
    isAnOrgaGroupSelected: false,
    departments: null,
    selectedDepartments: null,
    isFormInEditMode: false,
    isOrgaAlreadyExistingOnOtherPortal: false,
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
      if (data) {
        if (typeof data === 'string') {
          this.organization.name = data;
          this.isFormInEditMode = false;
        }
      } else {
        this.organization = {
          name: '',
          group: null,
          departments: [],
        };
        this.isFormInEditMode = false;
      }
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
          this.showOrgaGroupsresults = true;
          this.isAnOrgaGroupSelected = false;
          this.orgaGroupFound = [];
          api
            .get(searchOrganizationGroupsUrl(this.userInput))
            .then((response) => {
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
        throw new Error('Error while fetching organizations ', error);
      }
    },
    async showDepartments() {
      try {
        const response = await api.get(departmentsUrl());
        this.departments = response.data;
      } catch (error) {
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
        api
          .post(organizationGroupsUrl(), this.organization.group)
          .then((response) => {
            this.organization.group = response.data.id;
          });
      } catch (error) {
        throw new Error('Error while creating organization group ', error);
      }
    },
    createOrganization(isItReturningData = false) {
      this.formState.fields = {
        isOrgaName: this.organization.name !== '',
        isGroupNat: this.formState.fields.isGroupNat == 'true',
        isGroupNatName:
          this.organization.group !== null && this.formState.fields.isGroupNat,
      };
      this.formState.isSubmitted = true;

      if (
        (this.formState.fields.isGroupNatName &&
          this.formState.fields.isOrgaName) ||
        (!this.formState.fields.isGroupNat && this.formState.fields.isOrgaName)
      ) {
        api
          .post(organizationsUrl(), {
            ...this.organization,
            group_id: this.organization?.group?.id || this.organization?.group || null,
            // group_id: this.organization.group.id, // TODO : use this line when organization.group is an object not an id
          })
          .then((response) => {
            if (isItReturningData) {
              this.Modal.responseModal(response.data);
            } else {
              this.Modal.closeModal();
            }
          })
          .catch((error) => {
            if (
              error.response.data.name &&
              error.response.data.name[0] ===
                'Un objet organization avec ce champ Nom existe déjà.'
            ) {
              this.isOrgaAlreadyExistingOnOtherPortal = true;
            }
            throw new Error('Error while creating organization ', error);
          });
      }
    },
    updateOrganization(isItReturningData = false) {
      this.formState.fields = {
        isOrgaName: this.organization.name !== '',
        isGroupNat: this.formState.fields.isGroupNat == 'true',
        isGroupNatName:
          this.organization.group !== null && this.formState.fields.isGroupNat,
      };
      this.formState.isSubmitted = true;

      if (
        (this.formState.fields.isGroupNatName &&
          this.formState.fields.isOrgaName) ||
        (!this.formState.fields.isGroupNat && this.formState.fields.isOrgaName)
      ) {
        try {
          const payload = {
            ...this.organization,
            group_id: this.organization?.group?.id || this.organization?.group || null,
          };
          delete this.organization.group;
          api
            .patch(getOrganizationById(this.organization.id), payload)
            .then((response) => {
              if (isItReturningData) {
                this.Modal.responseModal(response.data);
              } else {
                this.Modal.closeModal();
                location.reload();
              }
            });
        } catch (error) {
          throw new Error('Error while updating organization ', error);
        }
      }
    },
    handleDepartmentsSelection(departments) {
      this.organization.departments = departments;
    },
    initCreateOrganizationModalData($event) {
      this.organization = { ...$event.detail };
      if (this.organization.id) {
        this.isFormInEditMode = true;
      }
      if (this.organization.group) {
        this.formState.fields.isGroupNat = true;
        this.isAnOrgaGroupSelected = true;
        this.userInput = this.organization.group.name;
      }
      if (this.organization.departments) {
        // If departments are already selected, we map them to their codes
        // selectedDepartments init them in the multiselect component
        // organization.departments is updated with the selected departments
        // so that it can be sent to the backend in the good format
        this.selectedDepartments = this.organization.departments.map(
          (department) => department.code
        );
        this.organization.departments = this.selectedDepartments;
      }
    },
  };
});
