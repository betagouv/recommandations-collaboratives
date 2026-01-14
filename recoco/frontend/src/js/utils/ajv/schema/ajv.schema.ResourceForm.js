import { minLengthErrorMessage, schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: FormResource
 */
export const schemaResourceFormValidator = {
  $id: '#/definitions/ResourceFormValidator',
  type: 'object',
  properties: {
    title: {
      type: 'string',
      minLength: 1,
      maxLength: 255,
      errorMessage: 'Le titre est requis (max 255 caractères)',
    },
    subtitle: {
      minLength: 1,
      type: 'string',
      maxLength: 500,
      errorMessage: 'Le sous-titre est requis (max 500 caractères)',
    },
    summary: {
      type: 'string',
      minLength: 1,
      maxLength: 500,
      errorMessage: 'Le résumé est requis (max 500 caractères)',
    },
    content: {
      type: 'string',
      minLength: 1,
      errorMessage: 'Le contenu est requis',
    },
    // status: {
    //   type: 'integer',
    //   minimum: 0,
    //   maximum: 10,
    // },
    category: {
      type: 'integer',
      minimum: 1,
      errorMessage: 'La catégorie est requise',
    },
    tags: {
      type: 'array',
      items: { type: 'string' },
      default: [],
    },
    support_orga: {
      type: 'string',
      minLength: 1,
      maxLength: 255,
      errorMessage: 'La structure porteuse est requise (max 255 caractères)',
    },
    departments: {
      type: 'array',
      items: { type: 'string', pattern: '^[0-9]{2,3}$' },
      minItems: 1,
      errorMessage: 'Au moins un département est requis',
    },
    expires_on: {
      type: 'string',
      format: 'date',
      errorMessage: "La date d'expiration est requise (format YYYY-MM-DD)",
    },
    contacts: {
      type: 'array',
      items: { type: 'integer' },
      default: [],
    },
  },
  required: [
    'category',
    'contacts',
    'content',
    'departments',
    'expires_on',
    // 'status',
    'subtitle',
    'summary',
    'support_orga',
    'tags',
    'title',
  ],
  definitions: schemaFormInputs,
};
