import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';
import { groupBy } from 'lodash/groupBy';

function SearchOrganisation() {
  return {
    orgaFound: [],
    orgaSorted: [],
    userInput: '',
    showOrgAsResults: false,
    selectedOrga: null,
    init() {},
    resetOrga() {
      this.userInput = '';
    },
    onSearch() {
      this.selectedOrga = null;
      if (this.userInput.length > 0) {
        this.orgaFound = [];
        api.get(searchOrganizationsUrl(this.userInput)).then((response) => {
          this.searchResults = response.data;
          this.orgaFound = this.searchResults.results;
          if (this.orgaFound.length > 0) {
            this.sortOrgasResults();
            this.showOrgAsResults = true;
          } else {
            this.showOrgAsResults = false;
          }
        });
      }
    },
    onSelectOrga(orga) {
      this.selectedOrga = orga;
      this.userInput = orga.name;
      this.showOrgAsResults = false;
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

      console.log(this.orgaFound);

      // const tempSortOrgas = Object.groupBy(this.orgaFound, ({group})=>group);
      const tempSortOrgas = _.groupBy(this.orgaFound, ({group})=>group);

      console.log(tempSortOrgas);

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
  };
}

Alpine.data('SearchOrganisation', SearchOrganisation);
