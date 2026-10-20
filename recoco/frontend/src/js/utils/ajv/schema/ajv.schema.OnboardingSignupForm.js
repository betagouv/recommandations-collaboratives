import {
  schemaFormInputs,
  maxLengthErrorMessage,
  minLengthErrorMessage,
} from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep1SignupFormValidator = {
  $id: '#/definitions/OnboardingStep1FormValidator',
  type: 'object',
  properties: {
    first_name: {
      allOf: [
        {
          type: 'string',
          minLength: 1,
          errorMessage: minLengthErrorMessage(1),
        },
        {
          type: 'string',
          maxLength: 128,
          errorMessage: maxLengthErrorMessage(128),
        },
      ],
    },
    last_name: {
      allOf: [
        {
          type: 'string',
          minLength: 1,
          errorMessage: minLengthErrorMessage(1),
        },
        {
          type: 'string',
          maxLength: 50,
          errorMessage: maxLengthErrorMessage(50),
        },
      ],
    },
    role: { $ref: '#/definitions/text' },
    email: { $ref: '#/definitions/email' },
    password1: { $ref: '#/definitions/passwordNormal' },
    password2: {
      allOf: [
        {
          type: 'string',
          const: { $data: '1/password1' },
          errorMessage: 'Doit correspondre au mot de passe.',
        },
      ]
    },
    phone: { $ref: '#/definitions/phone' },
  },
  required: ['first_name', 'last_name', 'role', 'email', 'password1', 'password2', 'phone'],
  definitions: schemaFormInputs,
};
