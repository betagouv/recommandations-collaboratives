import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep1FormValidator = {
  $id: '#/definitions/OnboardingStep1FormValidator',
  type: 'object',
  properties: {
    first_name: { $ref: '#/definitions/text' },
    last_name: { $ref: '#/definitions/text' },
    company_name: { $ref: '#/definitions/text' },
    role: { $ref: '#/definitions/text' },
    email_adress: { $ref: '#/definitions/email' },
    password: { $ref: '#/definitions/password' },
    phone_number: { $ref: '#/definitions/phone' },
  },
  required: [
    'first_name',
    'last_name',
    'org_name',
    'role',
    'email',
    'password',
    'phone',
  ],
  definitions: schemaFormInputs,
};