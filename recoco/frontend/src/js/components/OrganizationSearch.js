import Alpine from 'alpinejs';
import api, { searchOrganizationsUrl } from '../utils/api';
import {
  addClassIfNotExists,
  removeAndAddClassConditionaly,
} from '../utils/cssUtils';

function OrganizationSearch(
  currentOrganization,
  required = false,
  dsfr = false,
  requestMethod = 'GET'
) {
  return {
    organization: '',
    results: [],
    required: required,
    requestMethod: requestMethod,
    dsfr: dsfr,
    init() {
      this.organization = currentOrganization;
      if (this.organization) this.validateData(true);

      [('focusout', 'input')].forEach((event) => {
        this.$refs.organization.addEventListener(event, (e) => {
          const hadErrors = required && e.target.value.length < 2;
          removeAndAddClassConditionaly(
            hadErrors,
            e.target.parentElement,
            'fr-input-group--valid',
            'fr-input-group--error'
          );
        });
      });
    },
    validateData(submittedForm = false) {
      if (
        this.dsfr &&
        this.required &&
        (this.requestMethod === 'POST' || submittedForm)
      ) {
        if (this.organization) {
          addClassIfNotExists(
            this.$refs.organization.parentElement,
            'fr-input-group--valid'
          );
        } else {
          addClassIfNotExists(
            this.$refs.organization.parentElement,
            'fr-input-group--error'
          );
        }
      }
    },
    async handleOrganizationChange(e) {
      e.preventDefault();

      try {
        if (e.target.value.length > 2) {
          const json = await api.get(searchOrganizationsUrl(e.target.value));

          if (json.data.count > 0) {
            return (this.results = json.data.results);
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
