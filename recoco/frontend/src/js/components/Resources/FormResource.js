import Alpine from 'alpinejs';

import api, { resourcesUrl, resourceUrl } from '../../utils/api';
import { schemaResourceFormValidator } from '../../utils/ajv/schema/ajv.schema.FormResource';

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
            content: { text: content },                 // ✅ API string -> nested object
            status,
            category: category?.name ?? '',             // ✅ API object -> name (string)
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
      // this.validate();
      // if (this.errors.length > 0) {
      //   console.log('Errors:', this.errors);
      //   return;
      // }
      this.newRessourcePayload = {
        title: 'Mon titre',
        subtitle: 'Mon sous-titre',
        summary: 'Mon résumé',
        content: {
          text: 'Mon contenu',
        },
        status: 0,
        category: 1,
        tags: ['tag1', 'tag2'],
        support_orga: 'Mon structure porteuse',
        departments: ['01', '02'],
        expires_on: new Date().toISOString().split('T')[0],
        contacts: [],
      };
      console.log(this.newRessourcePayload);
      this.newRessourcePayload = {
        ...this.newRessourcePayload,
        content: this.newRessourcePayload.content.text,
      };
      if (resourceId) {
        api.put(resourceUrl(resourceId), this.newRessourcePayload)
          .then(response => {
            console.log('Resource updated:', response.data);
          })
          .catch(error => {
            console.error('Error updating resource:', error);
          });
      } else {
        api.post(resourcesUrl(), this.newRessourcePayload)
          .then(response => {
            console.log('Resource created:', response.data);
          })
          .catch(error => {
            console.error('Error creating resource:', error);
          });
      }
    },

    validate() {
      const fields = Object.keys(this.$refs.createResourceForm);
      const validateMap = {};
      fields.forEach((field) => {
        validateMap[field] = this.$refs.createResourceForm[field].value;
      });
      const validate = ajv.compile(schemaResourceFormValidator);
      const valid = validate(validateMap);
      if (valid) {
        this.errors = [];
      } else {
        this.errors = validate.errors;
      }
    },
  };
});
