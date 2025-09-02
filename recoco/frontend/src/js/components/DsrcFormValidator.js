import Alpine from 'alpinejs';

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import addErrors from 'ajv-errors';

const ajv = new Ajv({ allErrors: true });
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
    async init() {
      if (!this.schema) {
        console.error('Missing validation schema');
      }

      const currentForm = document.getElementById(formId);
      const fields = Object.keys(this.schema.properties);
      const fieldToCheck = [];

      fields.forEach((field) => {
        this.form[field] = {
          message_group: {
            messages: [],
          },
          errors: [],
          touched: false,
          changed: false,
          value: currentForm[field].value,
        };
        if (currentForm[field].value) fieldToCheck.push(field);
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
        document.getElementById(formId).addEventListener('submit', (event) => {
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
      document.getElementById(formId).setAttribute('novalidate', '');
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
        index === 0 && this.$refs[currentErrorField].focus();
        // Set the error class on the field

        this.form[currentErrorField].is_valid = false;
        this.form[currentErrorField].errors =
          this.getFieldErrors(currentErrorField);
        this.form[currentErrorField].valid_class = 'error';
      });
    },
    validateInput(event) {
      const fieldName = event.target.name;
      this.validate();
      this.form[fieldName].errors = this.getFieldErrors(fieldName);
      if (
        (this.form[fieldName].is_valid === false ||
          this.form[fieldName].is_valid === undefined) &&
        this.form[fieldName].errors.length === 0
      ) {
        this.form[fieldName].is_valid = true;
        this.form[fieldName].valid_class = 'valid';
      } else if (this.form[fieldName].errors.length > 0) {
        this.form[fieldName].is_valid = false;
        this.form[fieldName].valid_class = 'error';
      }
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
