/************************************************************************************
 * This file contains JSON schema for form validation with Ajv
 *
 * AJV Doc on Combining Schemas: https://ajv.js.org/guide/combining-schemas.html
 ************************************************************************************/

export function maxLengthErrorMessage(maxLength) {
  return `${maxLength} caractère${maxLength > 1 ? 's' : ''}  maximum`;
}

export function minLengthErrorMessage(minLength) {
  return `${minLength} caractère${minLength > 1 ? 's' : ''} minimum`;
}

/**
 * Password schema
 * Note: This schema only validates the required length and character classes. It does not guarantee password strength.
 */

/**
 * Common Schemas for form inputs.
 * Adjust as necessary for your form.
 */
export const schemaFormInputs = {
  text: {
    allOf: [
      {
        type: 'string',
        minLength: 3,
        errorMessage: minLengthErrorMessage(3),
      },
      {
        type: 'string',
        maxLength: 100,
        errorMessage: maxLengthErrorMessage(100),
      },
    ],
  },
  phone: {
    type: 'string',
    pattern: '[\\+0-9]{10,14}',
    errorMessage: {
      pattern: 'Veuillez rentrer un téléphone valide',
    },
  },
  email: {
    type: 'string',
    format: 'email',
    errorMessage: {
      format: 'Veuillez rentrer une adresse email valide',
    },
  },
  passwordStrict: {
    // TODO:Adapt for better password strength validation
    // See: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
    allOf: [
      {
        type: 'string',
        format: 'password',
        minLength: 12,
        errorMessage: minLengthErrorMessage(12),
      },
      {
        type: 'string',
        pattern: '[$\\-+!?*&%~_@#]{1}',
        errorMessage: '1 caractère spécial minimum',
      },
      {
        type: 'string',
        pattern: '[0-9]{1}',
        errorMessage: '1 chiffre minimum',
      },
    ],
  },
  passwordSoft: {
    // TODO:Adapt for better password strength validation
    // See: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
    allOf: [
      {
        type: 'string',
        format: 'password',
        minLength: 8,
        errorMessage: minLengthErrorMessage(8),
      },
    ],
  },
  passwordNormal: {
    allOf: [
      {
        type: 'string',
        format: 'password',
        minLength: 8,
        errorMessage: minLengthErrorMessage(8),
      },
      {
        type: 'string',
        pattern: '[0-9]{1}',
        errorMessage: '1 chiffre minimum',
      },
      {
        type: 'string',
        pattern: '[A-Z]{1}',
        errorMessage: '1 majuscule minimum',
      },
    ],
  },
  postcode: {
    // TODO : adapt for French postcode validation
    allOf: [
      {
        type: 'string',
        minLength: 5,
        errorMessage: minLengthErrorMessage(5),
      },
      {
        type: 'string',
        maxLength: 5,
        errorMessage: maxLengthErrorMessage(5),
      },
    ],
  },
  textarea: {
    type: 'string',
    maxLength: 200,
    errorMessage: {
      maxLength: maxLengthErrorMessage(200),
    },
  },
  checkbox: {
    type: 'string',
    pattern: 'on|true',
    errorMessage: {
      maxLength: maxLengthErrorMessage(200),
    },
  },
  select: { type: 'string' },
  disabled_field: { type: 'string' },
  radio_group: {
    type: 'string',
    pattern: 'on|true',
    errorMessage: {
      pattern: 'Erreur de validation: Choix unique',
    },
  },
  checkbox_group: {
    type: 'string',
    pattern: 'on|true',
    errorMessage: {
      pattern: 'Erreur de validation: Cases à cocher',
    },
  },
};
