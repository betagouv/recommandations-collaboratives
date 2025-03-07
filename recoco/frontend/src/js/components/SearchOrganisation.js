import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';

function SearchOrganisation() {
  return {
    orgaFound: [],
    orgaSorted: [],
    userInput: '',
    showOrgasresults: false,
    isAnOrgaSelected: false,
    init() {
    },
    onSearch() {
      this.isAnOrgaSelected = false;
      try {
        if (this.userInput.length > 0) {
          this.orgaFound = [];
          api.get(searchOrganizationsUrl(this.userInput)).then((response) => {
            this.searchResults = response.data;
            this.orgaFound = this.searchResults.results;
            if (this.orgaFound.length > 0) {
              this.sortOrgasResults();
              this.showOrgasresults = true;
            } else {
              this.showOrgasresults = false;
            }
          });
        }
      } catch (error) {
        console.log(error);
        throw new Error('Error while searching for organizations ', error);
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

      this.orgaSorted = [];
      this.orgaFound.sort((a, b) => {
        if (a.name < b.name) {
          return -1;
        }
        if (a.name > b.name) {
          return 1;
        }
        return 0;
      });

      const tempSortOrgas = Object.groupBy(this.orgaFound, ({group})=>group);

      for (const prop in tempSortOrgas) {
        if (tempSortOrgas[prop][0].group == null){
          for (let i = 0; i < tempSortOrgas[prop].length; i++){
            tempSortOrgas[prop][i].group = {name: 'AUTRES'};
          }
        }
        else {
          this.orgaSorted.push(tempSortOrgas[prop]);
        }
      }
      for (const prop in tempSortOrgas) {
        if (tempSortOrgas[prop][0].group.name === 'AUTRES'){
          this.orgaSorted.push(tempSortOrgas[prop]);
        }
      }
    },
    setSearch() {
      this.userInput = this.$store.contact.orgaSelected.name;
      this.showOrgasresults = false;
      this.isAnOrgaSelected = true;
    },
    resetSearch() {
      this.userInput = '';
      this.showOrgasresults = false;
      this.isAnOrgaSelected = false;
      this.$store.contact.orgaSelected = null;
    },
  };
}

Alpine.data('SearchOrganisation', SearchOrganisation);
