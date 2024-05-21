import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: SigninForm
 */
export const schemaOnboardingStep1SigninFormValidator = {
  $id: '#/definitions/OnboardingStep1SigninFormValidator',
  type: 'object',
  properties: {
    login: { $ref: '#/definitions/email' },
    password: { $ref: '#/definitions/passwordSoft' },
  },
  required: ['login', 'password'],
  definitions: schemaFormInputs,
};
