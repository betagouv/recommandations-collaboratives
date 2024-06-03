import { minLengthErrorMessage, schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: PrefillProjectForm
 */
export const schemaPrefillProjectFormValidator = {
  $id: '#/definitions/PrefillProjectFormValidator',
  type: 'object',
  properties: {
    name: { $ref: '#/definitions/text' },
    location: { $ref: '#/definitions/text' },
    // postcode: { $ref: '#/definitions/text' },
    description: {
      type: 'string',
      minLength: 3,
      errorMessage: minLengthErrorMessage(3),
    },
  },
  required: ['name', 'location', 'description'],
  definitions: schemaFormInputs,
};
