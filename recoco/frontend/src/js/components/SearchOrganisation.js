import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';

function SearchOrganisation() {
  return {
    orgaFound: [],
    userInput: '',
    showOrgasresults: false,
    isAnOrgaSelected: false,
    init() {},
    onSearch() {
      this.isAnOrgaSelected = false;
      if (this.userInput.length > 0) {
        this.orgaFound = [];
        api.get(searchOrganizationsUrl(this.userInput)).then((response) => {
          this.searchResults = response.data;
          this.orgaFound = this.searchResults.results;
          if (this.orgaFound.length > 0) {
            // this.sortOrgasResults();
            console.log('orgas found : ', this.orgaFound);
            this.showOrgasresults = true;
          } else {
            this.showOrgasresults = false;
          }
        });
      }
    },
    onSelectOrga(orga) {
      this.isAnOrgaSelected = true;
      this.selectedOrga = orga;
      this.userInput = orga.name;
      this.showOrgasresults = false;
      this.$store.contact.orgaSelected = orga;
    },
    sortOrgasResults() {
      this.orgaFound.sort((a, b) => {
        return (
          this.assignNullValueGroupOrgaAtEnd(a.group.name) -
          this.assignNullValueGroupOrgaAtEnd(b.group.name)
        );
      });
      console.log('orgas sorted : ', this.orgaFound);
    },
    assignNullValueGroupOrgaAtEnd(value) {
      if (value == null) {
        return 'zz';
      } else {
        return value;
      }
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
