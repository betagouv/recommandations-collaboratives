import { minLengthErrorMessage, schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: FormResource
 */
export const schemaResourceFormValidator = {
  $id: '#/definitions/ResourceFormValidator',
  type: 'object',
  properties: {
    category: { $ref: '#/definitions/int8' },
    contacts: {
      elements: {
        type: 'int8',
      },
    },
    content: { $ref: '#/definitions/text' },
    departments: {
      elements: {
        type: 'string',
      },
    },
    expires_on: { $ref: '#/definitions/date' },
    status: { $ref: '#/definitions/int8' },
    subtitle: { $ref: '#/definitions/text' },
    summary: { $ref: '#/definitions/text' },
    support_orga: { $ref: '#/definitions/text' },
    tags: { $ref: '#/definitions/array' },
    title: { $ref: '#/definitions/text' },
  },
  required: [
    'category',
    'contacts',
    'content',
    'departments',
    'expires_on',
    'status',
    'subtitle',
    'summary',
    'support_orga',
    'tags',
    'title',
  ],
  definitions: schemaFormInputs,
};
