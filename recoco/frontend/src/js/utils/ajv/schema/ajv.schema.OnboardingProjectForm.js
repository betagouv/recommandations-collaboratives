import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStepProjectFormValidator = {
  $id: '#/definitions/OnboardingStepProjectFormValidator',
  type: 'object',
  properties: {
    name: { $ref: '#/definitions/text' },
    location: { $ref: '#/definitions/text' },
    insee: { $ref: '#/definitions/text' },
    description: { $ref: '#/definitions/textarea' },
    response: { $ref: '#/definitions/textarea' },
  },
  required: ['name', 'location', 'insee', 'description', 'response'],
  definitions: schemaFormInputs,
};
