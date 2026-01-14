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
    resourceFormData: {
      title: null,
      subtitle: null,
      summary: null,
      content: {
        text: null,
      },
      status: 0,
      category: null,
      tags: [],
      support_orga: null,
      departments: [],
      expires_on: null,
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
      // this.initFormFields(this.$refs.formResource);
      if (resourceId) {
        // fetch resource data and populate resourcePayload
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

          this.resourceFormData = {
            // keep your exact payload shape
            title,
            subtitle,
            summary,
            content: { text: content }, // ✅ API string -> nested object
            status,
            category: category?.id ?? '', // ✅ API object -> name (string)
            tags,
            support_orga,
            departments,
            expires_on,
            contacts,
          };
          this.$dispatch('set-content', { text: content });

          console.log(this.resourceFormData);
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
    onSubmit(event) {
      event.preventDefault();
      this.submitted = true;

      /*/ *********** TEST DATA ***********

      this.resourceFormData = {
        title: 'Test',
        subtitle: 'dez',
        summary: 'dez',
        content: { text: 'dez' },
        status: 0,
        tags: [],
        support_orga: 'dezdez',
        departments: [
          '01',
          '03',
          '07',
          '15',
          '26',
          '43',
          '74',
          '38',
          '42',
          '63',
          '69',
          '73',
        ],
        expires_on: '2026-01-23',
        contacts: [],
        keywords: ['PRE_DRAFT'],
        category_id: '1',
      };
      // *********** END TEST DATA ************/

      console.log(this.resourceFormData);
      this.resourcePayload = {
        ...this.resourceFormData,
        content: this.resourceFormData.content.text,
        category: parseInt(this.newRessourcePayload.category),
        category_id: this.resourceFormData.category,
      };
      this.resourcePayload.contacts = this.resourceFormData.contacts.map((c) =>
        typeof c === 'object' ? c.id : c
      );
      delete this.resourcePayload.category;
      console.log('Payload to submit:', this.resourcePayload);
      if (resourceId) {
        api
          .put(resourceUrl(resourceId), this.resourcePayload)
          .then((response) => {
            console.log('Resource updated:', response.data);
          })
          .catch((error) => {
            console.error('Error updating resource:', error);
          });
      } else {
        api
          .post(resourcesUrl(), this.resourcePayload)
          .then((response) => {
            console.log('Resource created:', response.data);
          })
          .catch((error) => {
            console.error('Error creating resource:', error);
          });
      }
    },

    validate() {
      console.log('validate');
      // Build validation map from the reactive payload
      const validateMap = {
        title: this.resourcePayload.title,
        subtitle: this.resourcePayload.subtitle,
        summary: this.resourcePayload.summary,
        content:
          typeof this.resourcePayload.content === 'object'
            ? this.resourcePayload.content.text
            : this.resourcePayload.content,
        status: this.resourcePayload.status,
        category: parseInt(this.resourcePayload.category) || 0,
        tags: this.resourcePayload.tags || [],
        support_orga: this.resourcePayload.support_orga,
        departments: this.resourcePayload.departments || [],
        expires_on: this.resourcePayload.expires_on,
        contacts: (this.resourcePayload.contacts || []).map((c) =>
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
      // if (!this.$refs.formResource[field].dataset.dirty) return '';
      if (!this.submitted) return '';
      return this.hasFieldError(fieldName)
        ? 'fr-input-group--error'
        : 'fr-input-group--valid';
    },

    validateField(fieldName) {
      // Validate on blur/change for real-time feedback after first submit
      this.validate();
    },

    // validateField(field) {
    //   // Vérifier l'état
    //   const isPristine = !field.dataset.dirty;
    //   console.log(this.$refs.formResource[field].pristine);
    //   this.validate();
    // },

    // initFormFields(form) {
    //   form.querySelectorAll('input, textarea, select').forEach((field) => {
    //     field.addEventListener('input', () => {
    //       field.dataset.dirty = 'true';
    //     });
    //   });
    // },
  };
});
