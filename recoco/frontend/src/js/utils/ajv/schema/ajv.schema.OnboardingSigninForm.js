import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep1SigninFormValidator = {
  $id: '#/definitions/OnboardingStep1SigninFormValidator',
  type: 'object',
  properties: {
    email: { $ref: '#/definitions/email' },
    password: { $ref: '#/definitions/passwordSoft' },
  },
  required: ['email', 'password'],
  definitions: schemaFormInputs,
};
