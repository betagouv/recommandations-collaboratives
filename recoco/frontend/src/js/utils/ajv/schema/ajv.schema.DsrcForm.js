import { schemaFormInputs } from './ajv.schema.forms';

/**
 * Validation schema for the form: DsrcFormValidator
 */
export const schemaDsrcFormValidator = {
  $id: '#/definitions/DsrcFormValidator',
  type: 'object',
  properties: {
    sample_name: { $ref: '#/definitions/text' },
    sample_phone: { $ref: '#/definitions/phone' },
    sample_email: { $ref: '#/definitions/email' },
    sample_password: { $ref: '#/definitions/password' },
    sample_postcode: { $ref: '#/definitions/postcode' },
    sample_description: { $ref: '#/definitions/textarea' },
    sample_checkbox: { $ref: '#/definitions/checkbox' },
    sample_select: { $ref: '#/definitions/select' },
    sample_disabled_field: { $ref: '#/definitions/disabled_field' },
    sample_radio_group: { $ref: '#/definitions/radio_group' },
    sample_checkbox_group: { $ref: '#/definitions/checkbox_group' },
  },
  required: ['sample_name', 'sample_email', 'sample_password'],
  definitions: schemaFormInputs,
};
