import Alpine from 'alpinejs';

import api, { resourcesUrl, resourceUrl, contactUrl } from '../../utils/api';
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
      this.initFormFields(this.$refs.formResource);
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
    fetchContacts() {
      // fetch contact details for each contact id in newRessourcePayload.contacts
      const contactIds = this.newRessourcePayload.contacts;
      const contactPromises = contactIds.map((id) =>
        api.get(contactUrl(id))
      );
      Promise.all(contactPromises)
        .then((responses) => {
          this.newRessourcePayload.contacts = responses.map(
            (res) => res.data
          );
        }
        )
        .catch((error) => {
          console.error('Error fetching contacts:', error);
        });
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
        category: parseInt(this.resourceFormData.category),
      };
      this.resourcePayload.contacts = this.resourceFormData.contacts.map((c) =>
        typeof c === 'object' ? c.id : c
      );
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
        title: this.$refs.formResource['title'].value,
        subtitle: this.$refs.formResource['subtitle'].value,
        summary: this.$refs.formResource['summary'].value,
        content:
          typeof this.$refs.formResource['content'].value === 'object'
            ? this.$refs.formResource['content'].value.text
            : this.$refs.formResource['content'].value,
        category: parseInt(this.$refs.formResource['category'].value) || 0,
        tags: this.$refs.formResource['tags'].value || [],
        support_orga: this.$refs.formResource['support_orga'].value,
        departments: this.$refs.formResource['departments'].value || [],
        expires_on: this.$refs.formResource['expires_on'].value,
        // contacts: (this.$refs.formResource['contacts'].value || []).map((c) =>
        //   typeof c === 'object' ? c.id : c
        // ),
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

    // validateField(fieldName) {
    //   // Validate on blur/change for real-time feedback after first submit
    //   this.validate();
    // },

    validateField(field) {
      this.validate();
      if (
        !this.formFields[field.name].pristine &&
        (this.formFields[field.name]?.hasError || false)
      ) {
        this.formFields[field.name].className = 'fr-input-group--error';
      } else {
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
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field) return;

        ['change', 'blur'].forEach((event) => {
          field.addEventListener(event, (e) => {
            this.formFields[e.target.name].pristine = false;
            this.validateField(e.target);
          });
        });
        field.addEventListener('input', (e) => {
          if (this.formFields[e.target.name].pristine) return;
          this.validateField(e.target);
        });
      });
    },
  };
});
