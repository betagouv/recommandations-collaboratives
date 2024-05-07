import Alpine from 'alpinejs';
import {
  addClassIfNotExists,
  removeAndAddClassConditionaly,
} from '../utils/cssUtils';

function FieldValidator(required, value, submittedForm = false) {
  return {
    isRequired: required,
    value: value == 'None' ? '' : value,
    init() {
      this.validateData(submittedForm);
      ['focusout', 'input'].forEach((event) => {
        this.$el.addEventListener(event, (e) => {
          const errors = required && e.target.value.length < 1;
          removeAndAddClassConditionaly(
            errors,
            e.target.parentElement,
            'fr-input-group--valid',
            'fr-input-group--error'
          );
        });
      });
    },
    validateData(submittedForm = false) {
      if (this.isRequired && (this.requestMethod === 'POST' || submittedForm)) {
        if (this.value) {
          addClassIfNotExists(this.$el.parentElement, 'fr-input-group--valid');
        } else {
          addClassIfNotExists(this.$el.parentElement, 'fr-input-group--error');
        }
      }
    },
  };
}

Alpine.data('FieldValidator', FieldValidator);
