import Alpine from 'alpinejs';
import {
  addClassIfNotExists,
  removeAndAddClassConditionaly,
  removeClassIfExists,
} from '../utils/cssUtils';

Alpine.data('CitySearch', CitySearch);

function CitySearch(required = false, requestMethod = 'GET') {
  return {
    // other default properties
    isLoading: false,
    postal: null,
    cities: null,
    required: required,
    currentPostal: null,
    currentInsee: null,
    requestMethod: requestMethod,

    init() {
      ['focusout', 'input'].forEach((event) => {
        this.$refs.postcode.addEventListener(event, (e) => {
          const errors = required && e.target.value.length < 5;
          removeAndAddClassConditionaly(
            errors,
            e.target.parentElement,
            'fr-input-group--valid',
            'fr-input-group--error'
          );
        });
      });

      ['change'].forEach((event) => {
        this.$refs.insee.addEventListener(event, (e) => {
          console.log('insee change event', e.target.value);
          const errors = required && e.target.value == '';
          removeAndAddClassConditionaly(
            errors,
            e.target.parentElement,
            'fr-select-group--valid',
            'fr-select-group--error'
          );
        });
      });
    },
    validateData(submittedForm = false) {
      if (this.required && (this.requestMethod === 'POST' || submittedForm)) {
        addClassIfNotExists(
          this.$refs.postcode.parentElement,
          `fr-input-group--${this.currentPostal ? 'valid' : 'error'}`
        );

        addClassIfNotExists(
          this.$refs.insee.parentElement,
          `fr-select-group--${this.currentInsee ? 'valid' : 'error'}`
        );
      }
    },
    getPostcode(postcode, insee) {
      const postCodeString = JSON.parse(postcode.textContent);
      const inseeString = JSON.parse(insee.textContent);
      this.currentPostal = postCodeString;
      this.currentInsee = inseeString;

      if (postCodeString) this.postal = postCodeString;
      if (inseeString) this.fetchCities(inseeString);
    },
    fetchCities(currentInsee = null) {
      if (this.postal == '') return;

      this.isLoading = true;
      fetch(`/api/communes/?postal=${this.postal}`)
        .then((res) => res.json())
        .then((data) => {
          this.isLoading = false;
          this.cities = data;
          if (this.cities.length == 1) {
            removeAndAddClassConditionaly(
              true,
              this.$refs.insee.parentElement,
              'fr-select-group--error',
              'fr-select-group--valid'
            );
          } else {
            removeClassIfExists(
              this.$refs.insee.parentElement,
              'fr-select-group--valid'
            );
          }
        })
        .finally(() => {
          if (currentInsee) this.$refs.insee.value = currentInsee;
        });
    },
  };
}
