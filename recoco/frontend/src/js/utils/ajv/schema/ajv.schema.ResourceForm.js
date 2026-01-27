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
      maxLength: 256,
      errorMessage: 'Le titre est limité à 256 caractères',
    },
    subtitle: {
      type: 'string',
      maxLength: 512,
      errorMessage: 'Le sous-titre est limité à 512 caractères',
    },
    summary: {
      type: 'string',
      maxLength: 512,
      errorMessage: 'Le résumé est limité à 512 caractères',
    },
    content: {
      type: 'string',
      minLength: 1,
      errorMessage: 'Le contenu est requis',
    },
    support_orga: {
      type: 'string',
      maxLength: 256,
      errorMessage: 'La nom de la structure porteuse est limitée à 256 caractères',
    },
    expires_on: {
      type: 'string',
      format: 'date',
      errorMessage: "La date d'expiration doit être au format YYYY-MM-DD",
    },
  },
  required: [
    'content',
    'title',
  ],
  definitions: schemaFormInputs,
};
