import Alpine from 'alpinejs';

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import addErrors from 'ajv-errors';

const ajv = new Ajv({ allErrors: true, $data: true });
addFormats(ajv);
addErrors(ajv);
/**
 * Use this Alpine component to provide frontend validation capabilities to a form rendered by the server.
 * @param {string} formId The id of the <form> element
 * @param {Object} formData The serialized form data from the server, defined in `forms.py` and serialized in `views.py`
 * @param {string} validationFunctionName The name of the AJV validation function to use. It should be generated into `ajv.validations.default.js` by the script `build:ajv` (`DsrcFormValidationFunction` is the default validation function for DsrcExampleForm). To Change the default validation function, add the schema for your form to `ajv.schema.forms.cjs` and run `npm run build:ajv`
 * @returns an Alpine component object containing the form data and methods to validate and handle form submission
 */
function DsrcFormValidator(formId, validationSchema, requestMethod = 'GET') {
  return {
    form: {},
    errors: [],
    schema: validationSchema,
    isFormEdited: false,
    canSubmit: true,
    submittedForm: requestMethod === 'POST',
    formElement: null,
    async init() {
      if (!this.schema) {
        console.error('Missing validation schema');
      }

      this.formElement = document.getElementById(formId);
      const fields = Object.keys(this.schema.properties);
      const fieldToCheck = [];

      fields.forEach((field) => {
        this.form[field] = {
          message_group: {
            help_text: '',
            messages: this.getFieldRuleMessages(field).map((text) => ({
              text,
              type: 'info',
            })),
          },
          errors: [],
          touched: false,
          changed: false,
          value: this.formElement[field].value,
        };
        if (this.formElement[field].value) fieldToCheck.push(field);
      });
      fieldToCheck.forEach((field) => {
        this.validateInput({ target: { name: field } });
      });

      // Display errors if the form was submitted with
      if (this.submittedForm) {
        this.validate();
        this.displayErrorsAndValidation();
      }

      this.$nextTick(() => {
        // enable form validation for all submission types (click, keyboard, ...)
        this.formElement.addEventListener('submit', (event) => {
          this.isFormEdited = false;
          this.canSubmit = false;
          this.submittedForm = true;
          this.validate();
          if (Array.isArray(this.errors) && this.errors.length > 0) {
            event.preventDefault();
            this.displayErrorsAndValidation();
          }
        });
      });
      this.customFocus();
      // Disable browser validation as we are using our own
      this.formElement.setAttribute('novalidate', '');
      // Let the server know that JS is enabled
      document.getElementById(`${formId}_js_enabled`).value = 'true';
    },

    validate() {
      const fields = Object.keys(this.form);
      const validateMap = {};
      fields.forEach((field) => {
        validateMap[field] = this.form[field].value;
      });
      const validate = ajv.compile(validationSchema);
      const valid = validate(validateMap);
      if (valid) {
        this.errors = [];
      } else {
        this.errors = validate.errors;
      }
    },
    getFieldErrors(fieldName) {
      const errors = this.errors.filter(
        (error) => error.instancePath.substring(1) === fieldName
      );
      return errors.map((error) => error.message);
    },
    getFieldRuleMessages(fieldName) {
      let definition = this.schema.properties[fieldName];

      // usefull when properties get shared definitions, ex: $ref: '#/definitions/passwordNormal'
      if (definition.$ref) {
        const definitionName = definition.$ref.replace('#/definitions/', '');
        definition = this.schema.definitions?.[definitionName];
      }

      const rules = definition?.allOf ?? [];
      return rules.map((rule) => rule.errorMessage);
    },
    setFieldMessages(fieldName) {
      const field = this.form[fieldName];
      if (!field.message_group || !field.message_group.messages) {
        field.message_group = { help_text: '', messages: [] };
      }
      let filteredMessages = [];
      if (
        field.message_group.messages.length === 0 &&
        field.errors.length > 0
      ) {
        filteredMessages = (field.errors || []).map((error) => ({
          text: error,
          type: 'error',
        }));
      } else {
        // If the field has a message_group set by the server: match local messages with error messages and set the message type accordingly
        filteredMessages = field.message_group.messages.reduce(
          (updatedMessages, message) => {
            if (field.errors.includes(message.text)) {
              message.type = 'error';
            } else {
              message.type = 'valid';
            }
            return [...updatedMessages, message];
          },
          []
        );
      }
      field.message_group.messages = filteredMessages;
    },
    fieldHasError(fieldName) {
      const field = this.form[fieldName];
      return field.touched === true && field.errors.length > 0;
    },
    displayErrorsAndValidation() {
      // Display error messages on each fields
      for (const field in this.form) {
        this.form[field].is_valid = true;
        this.form[field].errors = [];
        this.form[field].valid_class = 'valid';
      }

      this.errors.forEach((error, index) => {
        const currentErrorField = error.instancePath.substring(1);
        // Set the focus on the first field with an error
        index === 0 && this.formElement[currentErrorField]?.focus();
        // Set the error class on the field

        this.form[currentErrorField].is_valid = false;
        this.form[currentErrorField].errors =
          this.getFieldErrors(currentErrorField);
        this.form[currentErrorField].valid_class = 'error';
      });

      for (const field in this.form) {
          this.setFieldMessages(field);
        }
    },
    validateInput(event) {
      this.validate();
      const fieldName = event.target.name;
      for (const name in this.form) {
        if (name === fieldName || this.form[name].changed) this.updateFieldState(name);
      }
    },
    updateFieldState(fieldName) {
      const field = this.form[fieldName];
      field.errors = this.getFieldErrors(fieldName);
      const hasErrors = field.errors.length > 0;
      field.is_valid = !hasErrors;
      field.valid_class = hasErrors ? 'error' : 'valid';

      this.setFieldMessages(fieldName);
    },
    touchInput(event) {
      const field = event.target.name;
      this.form[field].touched = true;
    },
    changeInput(event) {
      const field = event.target.name;
      this.form[field].changed = true;
      // validate the field when it changes: remove this if you want to validate the form only on `blur` or `submit` events
      // Use a debounce mechanism for slow/complex/async validations (e.g. API calls)
      this.validateInput(event);
    },
    customFocus() {
      const elementToFocus = this.$el.querySelector('.element-to-focus');
      if (!elementToFocus) return;
      elementToFocus.parentElement.querySelector('input').focus();
    },
  };
}

Alpine.data('DsrcFormValidator', DsrcFormValidator);
