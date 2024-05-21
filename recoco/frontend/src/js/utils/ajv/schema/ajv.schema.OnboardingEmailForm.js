import { schemaFormInputs } from './ajv.schema.forms';

export const schemaOnboardingEmailFormValidator = {
  $id: '#/definitions/OnboardingEmailFormValidator',
  type: 'object',
  properties: {
    email: { $ref: '#/definitions/email' },
  },
  required: ['email'],
  definitions: schemaFormInputs,
};
