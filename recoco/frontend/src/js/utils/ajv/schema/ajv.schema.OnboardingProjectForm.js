import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep2ProjectFormValidator = {
  $id: '#/definitions/OnboardingStep2ProjectFormValidator',
  type: 'object',
  properties: {
    name: { $ref: '#/definitions/text' },
    location: { $ref: '#/definitions/text' },
    description: { $ref: '#/definitions/textarea' },
    response: { $ref: '#/definitions/textarea' },
  },
  required: ['name', 'location', 'description', 'response'],
  definitions: schemaFormInputs,
};
