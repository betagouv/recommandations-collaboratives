import Alpine from 'alpinejs';

import api, { resourceUrl, contactUrl } from '../../utils/api';
import { schemaResourceFormValidator } from '../../utils/ajv/schema/ajv.schema.ResourceForm';

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import addErrors from 'ajv-errors';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);
addErrors(ajv);

Alpine.data('FormResource', (resourceId) => {
  return {
    is_draft: true,
    errors: [],
    formFields: {},
    submitted: false,
    resourceFormData: {
      title: null,
      subtitle: null,
      summary: null,
      content: {
        text: null,
      },
      status: 0,
      category: "",
      tags: [],
      support_orga: null,
      departments: [],
      expires_on: null,
      contacts: [],
    },
    init() {
      Alpine.nextTick(() => {
        this.initFormFields(this.$refs.formResource);
      });

      if (resourceId) {
        // fetch resource data and populate resourcePayload
        api.get(resourceUrl(resourceId)).then((response) => {
          const {
            title = '',
            subtitle = '',
            summary = '',
            content = '',
            status = 0,
            category = null,
            tags = [],
            support_orga = '',
            departments = [],
            expires_on = '',
            contacts = [],
          } = response.data;

          this.resourceFormData = {
            // keep your exact payload shape
            title,
            subtitle,
            summary,
            content: { text: content },
            status,
            category: category?.id ?? '', // ✅ API object -> name (string)
            tags,
            support_orga,
            departments,
            expires_on,
            contacts,
          };
          this.$dispatch('set-content', { text: content });
          this.fetchContacts();

          console.log(this.resourceFormData);
        });
      }
    },
    fetchContacts() {
      // fetch contact details for each contact id in resourceFormData.contacts
      const contactIds = this.resourceFormData.contacts;
      const contactPromises = contactIds.map((id) =>
        api.get(contactUrl(id))
      );
      Promise.all(contactPromises)
        .then((responses) => {
          this.resourceFormData.contacts = responses.map(
            (res) => res.data
          );
        }
        )
        .catch((error) => {
          console.error('Error fetching contacts:', error);
        });
    },
    closeCreateContactModal(event) {
      if (event.target.id !== 'search-contact-modal' && event.target.id !== '') {
        return;
      }
      const contact = event.detail;
      // avoid duplicates
      const exists = this.resourceFormData.contacts.some(
        (c) => c.id === contact.id
      );
      if (!exists) {
        this.resourceFormData.contacts = [
          ...this.resourceFormData.contacts,
          contact,
        ];
      } else {
        console.log('Contact already exists in the resource');
        // TODO : show a message to the user
      }
    },
    onSubmit() {
      this.submitted = true;

      // Validate the form using AJV
      const isValid = this.validate();
      if (!isValid) {
        return;
      }

      // Form is valid - let the standard form submission proceed
      // The hidden fields will carry the complex data (status, content, contacts)
      this.$nextTick(() => {
        this.$refs.formResource.submit();
      });
    },

    validate() {
      // Build validation map from the reactive payload
      const validateMap = {
        title: this.$refs.formResource['title'].value,
        subtitle: this.$refs.formResource['subtitle'].value,
        summary: this.$refs.formResource['summary'].value,
        content: Alpine.raw(this.$store.editor.currentMessage),
        category: parseInt(this.$refs.formResource['category'].value) || 0,
        tags: this.$refs.formResource['tags'].value,
        support_orga: this.$refs.formResource['support_orga'].value,
        expires_on: this.$refs.formResource['expires_on'].value,
      };

      const validate = ajv.compile(schemaResourceFormValidator);
      const valid = validate(validateMap);

      if (valid) {
        this.errors = [];
      } else {
        this.errors = validate.errors;
      }

      // Update formFields for per-field error tracking
      this.updateFormFieldsErrors();

      return valid;
    },

    updateFormFieldsErrors() {
      // Reset all field errors
      const fieldNames = Object.keys(schemaResourceFormValidator.properties);
      fieldNames.forEach((field) => {
        if (!this.formFields[field]) {
          this.formFields[field] = { errors: [], hasError: false };
        }
        this.formFields[field].errors = [];
        this.formFields[field].hasError = false;
      });

      // Map errors to their respective fields
      this.errors.forEach((error) => {
        const fieldName = error.instancePath.substring(1);
        if (fieldName && this.formFields[fieldName]) {
          this.formFields[fieldName].errors.push(error.message);
          this.formFields[fieldName].hasError = true;
          this.formFields[fieldName].className = 'fr-input-group--error';
        }
      });
    },

    getFieldErrors(fieldName) {
      if (this.formFields[fieldName]?.pristine && !this.submitted) return [];
      return this.formFields[fieldName]?.errors || [];
    },

    validateField(field) {
      this.validate();
      if (
        (!this.formFields[field.name].pristine) &&
        this.formFields[field.name]?.hasError
      ) {
        this.formFields[field.name].className = 'fr-input-group--error';
      } else if (!this.formFields[field.name]?.hasError) {
        this.formFields[field.name].className = 'fr-input-group--valid';
      }
    },

    initFormFields(form) {
      const fieldNames = Object.keys(schemaResourceFormValidator.properties);
      fieldNames.forEach((fieldName) => {
        this.formFields[fieldName] = {
          pristine: true,
          className: '',
        };
        if (fieldName !== 'content') {
          const field = form.querySelector(`[name="${fieldName}"]`);
          if (!field) return;

          ['change', 'blur'].forEach((event) => {
            field.addEventListener(event, (e) => {
              this.formFields[e.target.name].pristine = false;
              this.validateField(e.target);
            });
          });
          field.addEventListener('input', (e) => {

            this.validateField(e.target);
          });
        } else {
          Alpine.raw(this.$store.editor.editorInstance).on('update', () => {
            this.formFields[fieldName].pristine = false;
            this.validateField({ name: 'content' });
          });
        }
      });
    },
    suppressContact(contact) {
      this.resourceFormData.contacts = this.resourceFormData.contacts.filter(
        (c) => c.id !== contact.id
      );
    }
  };
});
