import Alpine from 'alpinejs';

import api, { resourcesUrl, resourceUrl } from '../../utils/api';
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
    keywords_options: [],
    errors: [],
    formFields: {},
    submitted: false,
    newRessourcePayload: {
      title: '',
      subtitle: '',
      summary: '',
      content: {
        text: '',
      },
      status: 0,
      category: '',
      tags: [],
      support_orga: '',
      departments: [],
      expires_on: '',
      contacts: [],
    },
    options: [
      {
        value: 'PRE_DRAFT',
        text: 'Incomplet',
      },
      {
        value: 'DRAFT',
        text: 'A modérer',
      },
      {
        value: 'TO_PROCESS',
        text: 'A traiter',
      },
      {
        value: 'VALIDATED',
        text: 'Validé',
      },
      {
        value: 'REJECTED',
        text: 'Refusé',
      },
    ],
    init() {
      console.log('FormResource');
      if (resourceId) {
        // fetch resource data and populate newRessourcePayload
        api.get(resourceUrl(resourceId)).then((response) => {
          console.log('Fetched resource data:', response.data);
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

          this.newRessourcePayload = {
            // keep your exact payload shape
            title,
            subtitle,
            summary,
            content: { text: content }, // ✅ API string -> nested object
            status,
            category: category?.name ?? '', // ✅ API object -> name (string)
            tags,
            support_orga,
            departments,
            expires_on,
            contacts,
          };

          console.log(this.newRessourcePayload);
        });
      }
      this.fetchKeywords();
    },
    fetchKeywords() {
      // api.get('/keywords').then(response => {
      //   this.keywords_options = response.data;
      // });
      this.keywords_options = [
        {
          id: 1,
          text: 'Environnement',
          value: 'environnement',
          search: 'environnement',
        },
        { id: 2, text: 'Économie', value: 'economie', search: 'economie' },
        { id: 3, text: 'Social', value: 'social', search: 'social' },
      ];
    },
    closeCreateContactModal(event) {
      const contact = event.detail;
      // avoid duplicates
      const exists = this.newRessourcePayload.contacts.some(
        (c) => c.id === contact.id
      );
      if (!exists) {
        this.newRessourcePayload.contacts = [
          ...this.newRessourcePayload.contacts,
          contact,
        ];
      } else {
        console.log('Contact already exists in the resource');
        // TODO : show a message to the user
      }
    },
    onSubmit(event) {
      event.preventDefault();
      this.submitted = true;
      const isValid = this.validate();

      if (!isValid) {
        return;
      }

      console.log(this.newRessourcePayload);
      this.newRessourcePayload = {
        ...this.newRessourcePayload,
        content: this.newRessourcePayload.content.text,
      };
      if (resourceId) {
        api
          .put(resourceUrl(resourceId), this.newRessourcePayload)
          .then((response) => {
            console.log('Resource updated:', response.data);
          })
          .catch((error) => {
            console.error('Error updating resource:', error);
          });
      } else {
        api
          .post(resourcesUrl(), this.newRessourcePayload)
          .then((response) => {
            console.log('Resource created:', response.data);
          })
          .catch((error) => {
            console.error('Error creating resource:', error);
          });
      }
    },

    validate() {
      // Build validation map from the reactive payload
      const validateMap = {
        title: this.newRessourcePayload.title,
        subtitle: this.newRessourcePayload.subtitle,
        summary: this.newRessourcePayload.summary,
        content:
          typeof this.newRessourcePayload.content === 'object'
            ? this.newRessourcePayload.content.text
            : this.newRessourcePayload.content,
        status: this.newRessourcePayload.status,
        category: parseInt(this.newRessourcePayload.category) || 0,
        tags: this.newRessourcePayload.tags || [],
        support_orga: this.newRessourcePayload.support_orga,
        departments: this.newRessourcePayload.departments || [],
        expires_on: this.newRessourcePayload.expires_on,
        contacts: (this.newRessourcePayload.contacts || []).map((c) =>
          typeof c === 'object' ? c.id : c
        ),
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
        }
      });
    },

    getFieldErrors(fieldName) {
      if (!this.submitted) return [];
      return this.formFields[fieldName]?.errors || [];
    },

    hasFieldError(fieldName) {
      if (!this.submitted) return false;
      return this.formFields[fieldName]?.hasError || false;
    },

    getFieldGroupClass(fieldName) {
      if (!this.submitted) return '';
      return this.hasFieldError(fieldName) ? 'fr-input-group--error' : '';
    },

    validateField(fieldName) {
      // Validate on blur/change for real-time feedback after first submit
      if (this.submitted) {
        this.validate();
      }
    },
  };
});
