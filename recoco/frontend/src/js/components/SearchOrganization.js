import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';
import _ from 'lodash';

Alpine.data('SearchOrganization', () => ({
  orgaFound: [],
  orgaSorted: [],
  userInputSearchOrganization: '',
  showOrgAsResults: false,
  selectedOrga: null,
  focusOnInput: false,
  init() {},
  onSearch() {
    this.focusOnInput = true;
    Alpine.$data(this.$el.parentElement).formState.fields.isOrgaSelected =
      false;
    this.selectedOrga = null;
    try {
      if (this.userInputSearchOrganization.length > 0) {
        this.orgaFound = [];
        api
          .get(searchOrganizationsUrl(this.userInputSearchOrganization))
          .then((response) => {
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
    } catch (error) {
      console.log(error);
      throw new Error('Error while searching for organizations ', error);
    }
  },
  onSelectOrga(orga) {
    this.selectedOrga = orga;
    this.userInput = orga.name;
    this.showOrgAsResults = false;
    this.$dispatch('set-organization', orga);
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

    const tempSortOrgas = _.groupBy(this.orgaFound, (orga) => orga.group);

    for (const prop in tempSortOrgas) {
      if (tempSortOrgas[prop][0].group == null) {
        for (let i = 0; i < tempSortOrgas[prop].length; i++) {
          tempSortOrgas[prop][i].group = { name: 'AUTRES' };
        }
      } else {
        this.orgaSorted.push(tempSortOrgas[prop]);
      }
    }
    for (const prop in tempSortOrgas) {
      if (tempSortOrgas[prop][0].group.name === 'AUTRES') {
        this.orgaSorted.push(tempSortOrgas[prop]);
      }
    }
  },
  handleDisplayOrganizationCreated(organization) {
    if (organization.name) {
      this.userInput = organization.name;
    }
  },
}));
