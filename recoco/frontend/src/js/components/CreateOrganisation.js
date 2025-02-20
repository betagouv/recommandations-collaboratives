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
    init() {
        this.showDepartments();

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
            console.log('orgaGroupsFound', this.orgaGroupsFound);
          } else {
            this.showOrgaGroupsresults = false;
          }
        });
      }
    },
    showDepartments() {
      api.get(departmentsUrl()).then((response) => {
        this.departments = response.data;
      });
      // forEach(this.departments, (department) => {
      //   department.selected = false;
      // });
      this.departments.forEach((department) => {
        department.selected = false;
      });
    },
    onSelectGroup(group) {
      this.isAnOrgaGroupSelected = true;
      this.organisationGroup = group;
      this.userInput = group.name;
      this.showOrgaGroupsresults = false;
    //   this.$store.contact.groupSelected = group;
    },
    createOrganisationGroup() {
      this.organisationGroup = {
        name: this.userInput,
      };
      this.isAnOrgaGroupSelected = true;
      this.showOrgaGroupsresults = false;
      api.post(organizationGroupsUrl(), this.organisationGroup).then((response) => {
                this.organisationGroup = response.data;
                // this.$store.contact.createdOrganisation = this.organisationToCreate;
                console.log(this.organisationGroup);
            });
    },
    selectThisDepartment(event) {

        console.log('departmentCode', event.target.value);
        // this.selectedDepartments = [...this.selectedDepartments,department];
        // console.log('selectedDepartment', this.selectedDepartments);
    },
    createOrganisation() {
        // if (this.$store.contact.groupSelected) {
        //   this.organisationGroup = this.$store.contact.groupSelected;
        //   this.verifOrga = false;
        // }
        this.selectedDepartments = ["01"];
        console.log('organisationGroup', this.organisationGroup);

        if(this.isGroupNat && this.organisationGroup === null){
          alert('Veuillez selectionner un groupe');
          this.orgaToCreateFormIsOk = false;
        }

        if (this.organisationName.length === 0) {
          this.verifNomOrga = true;
        }
        else {
          this.verifNomOrga = false;
          if (this.organisationGroup === null) {
            this.organisationToCreate = {
                name: this.organisationName,
              };
          }
          else {
              this.organisationToCreate = {
                name: this.organisationName,
                group: this.organisationGroup.id,
                departments: this.selectedDepartments,
              };
          }
            api.post(organizationsUrl(), this.organisationToCreate).then((response) => {
                this.organisationToCreate = response.data;
                this.$store.contact.createdOrganisation = this.organisationToCreate;
                console.log(this.organisationToCreate);
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
