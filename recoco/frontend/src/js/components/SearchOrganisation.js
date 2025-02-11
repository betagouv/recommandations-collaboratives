import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';

function SearchOrganisation() {
  return {
    orgaFound: [],
    userInput: '',
    showOrgasresults: false,
    isAnOrgaSelected: false,
    init() {
    },
    onSearch() {
      console.log('onSearch');
      if (this.userInput.length > 0) {
        this.orgaFound = [];
        api.get(searchOrganizationsUrl(this.userInput)).then((response) => {
          this.searchResults = response.data;
          this.orgaFound = this.searchResults.results;
          console.log('orgaFound : ', this.orgaFound);
            if(this.orgaFound.length > 0) {
              this.showOrgasresults = true;
            }
            else {
              this.showOrgasresults = false;
            }
          });
      }
    },
    onSelectOrga(orga) {
      console.log('mon orga : ', orga);
      this.isAnOrgaSelected = true;
      this.selectedOrga = orga;
      this.userInput = orga.name;
      this.showOrgasresults = false;
      this.$store.contact.orgaSelected = orga;
    },
    // closeModal() {
    //   this.isAContactSelected = false;
    //   this.showContactsresults = false
    //   this.userInput = '';
    //   this.isOpenCreateContactModal = false;
    // },
    // onCancelSelectContact(){
    //   this.isAContactSelected=false;
    //    this.selectedContact = null;
    // }
  };
}

Alpine.data('SearchOrganisation', SearchOrganisation);
