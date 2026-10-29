import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';

function OrganizationSearch(currentOrganization) {
  return {
    organization: currentOrganization,
    results: [],
    async handleOrganizationChange(e) {
      e.preventDefault();

      try {
        if (e.target.value.length > 2) {
          const response = await api.get(
            searchOrganizationsUrl(e.target.value)
          );
          if (response && response.data) {
            return (this.results = response.data.results);
          }
        } else {
          return (this.results = []);
        }
      } catch (errors) {
        console.error('errors in organization search : ', errors);
      }
    },
    handleResultClick(result) {
      this.organization = result;
    },
  };
}

Alpine.data('OrganizationSearch', OrganizationSearch);
