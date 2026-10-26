import {
  schemaFormInputs,
  maxLengthErrorMessage,
  minLengthErrorMessage,
} from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaAdvisorSignupFormValidator = {
  $id: '#/definitions/AdvisorSignupFormValidator',
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
    organization_position: { $ref: '#/definitions/text' },
    email: { $ref: '#/definitions/email' },
    phone_no: { $ref: '#/definitions/phone' },
    password1: { $ref: '#/definitions/passwordNormal' },
    password2: {
      allOf: [
        {
          type: 'string',
          const: { $data: '1/password1' },
          errorMessage: 'Doit correspondre au mot de passe.',
        },
      ],
    },
  },
  required: [
    'first_name',
    'last_name',
    'organization_position',
    'email',
    'phone_no',
    'password1',
    'password2',
  ],
  definitions: schemaFormInputs,
};
