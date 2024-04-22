import { schemaFormInputs } from './ajv.schema.forms';

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
    description: { $ref: '#/definitions/text' },
  },
  required: ['name', 'location', 'description'],
  definitions: schemaFormInputs,
};
