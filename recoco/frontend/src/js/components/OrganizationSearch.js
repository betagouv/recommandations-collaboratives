import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';
import { removeAndAddClassConditionaly } from '../utils/cssUtils';

function OrganizationSearch(currentOrganization, required = false) {
  return {
    organization: '',
    results: [],
    required: false,
    init() {
      this.organization = currentOrganization;
      ['focusout', 'input'].forEach((event) => {
        this.$refs.organization.addEventListener(event, (e) => {
          const errors = required && e.target.value.length < 2;
          removeAndAddClassConditionaly(
            errors,
            e.target.parentElement,
            'fr-input-group--valid',
            'fr-input-group--error'
          );
        });
      });
    },
    async handleOrganizationChange(e) {
      e.preventDefault();

      try {
        if (e.target.value.length > 2) {
          const results = await api.get(searchOrganizationsUrl(e.target.value));

          if (results && results.data) {
            return (this.results = results.data);
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
