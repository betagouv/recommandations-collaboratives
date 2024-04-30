import Alpine from 'alpinejs';
import {
  removeAndAddClassConditionaly,
  removeClassIfExists,
} from '../utils/cssUtils';

Alpine.data('CitySearch', CitySearch);

function CitySearch(required = false) {
  return {
    // other default properties
    isLoading: false,
    postal: null,
    cities: null,
    required: required,

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
            'fr-input-group--valid',
            'fr-input-group--error'
          );
        });
      });
    },
    getPostcode(postcode, insee) {
      const postCodeString = JSON.parse(postcode.textContent);
      const inseeString = JSON.parse(insee.textContent);

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
              'fr-input-group--error',
              'fr-input-group--valid'
            );
          } else {
            removeClassIfExists(
              this.$refs.insee.parentElement,
              'fr-input-group--valid'
            );
          }
        })
        .finally(() => {
          if (currentInsee) this.$refs.insee.value = currentInsee;
        });
    },
  };
}
