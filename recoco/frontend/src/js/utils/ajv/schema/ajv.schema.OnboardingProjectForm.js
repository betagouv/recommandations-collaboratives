import { minLengthErrorMessage, schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep2ProjectFormValidator = {
  $id: '#/definitions/OnboardingStep2ProjectFormValidator',
  type: 'object',
  properties: {
    name: { $ref: '#/definitions/text' },
    location: { $ref: '#/definitions/text' },
    description: {
      type: 'string',
      minLength: 3,
      errorMessage: minLengthErrorMessage(3),
    },
  },
  required: ['name', 'location', 'description'],
  definitions: schemaFormInputs,
};
