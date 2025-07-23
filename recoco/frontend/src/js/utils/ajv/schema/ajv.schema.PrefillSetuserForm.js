import {
  schemaFormInputs,
  maxLengthErrorMessage,
  minLengthErrorMessage,
} from './ajv.schema.forms';

/**
 * Validation schema for the form: OnboardingPrefillSignup
 */
export const schemaOnboardingPrefillSetuserFormValidator = {
  $id: '#/definitions/OnboardingPrefillSetuserFormValidator',
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
    message: { $ref: '#/definitions/text' },
    email: { $ref: '#/definitions/email' },
    phone: { $ref: '#/definitions/phone' },
  },
  required: ['first_name', 'last_name', 'role', 'email', 'phone'],
  definitions: schemaFormInputs,
};
