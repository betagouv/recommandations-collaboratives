import { minLengthErrorMessage, schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaOnboardingStep2ProjectFormValidator = {
  $id: '#/definitions/OnboardingStep2ProjectFormValidator',
  type: 'object',
  properties: {
    name: { $ref: '#/definitions/text' },
    location: {
      type: 'string',
    },
    email: {
      type: 'string',
      format: 'email',
      errorMessage: {
        format: "L'adresse email doit être au format prenom.nom@domaine.fr",
      },
    },
    description: {
      type: 'string',
      minLength: 3,
      errorMessage: minLengthErrorMessage(3),
    },
  },
  required: ['name', 'description', 'email'],
  definitions: schemaFormInputs,
};
