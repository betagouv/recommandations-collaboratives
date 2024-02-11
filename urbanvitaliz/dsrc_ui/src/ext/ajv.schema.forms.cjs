/************************************************************************************
 * This file contains JSON schema for form validation with Ajv
 *
 * AJV Doc on Combining Schemas: https://ajv.js.org/guide/combining-schemas.html
 ************************************************************************************/

/**
 * Common Schemas for form inputs.
 */
const schemaFormInputs = {
	text: { type: 'string', minLength: 1, maxLength: 40 },
	phone: { type: 'string', minLength: 8, maxLength: 16 },
	email: { type: 'string', format: 'email' },
	password: { type: 'string', format: 'password', minLength: 12, maxLength: 40 },
	postcode: { type: 'string', minLength: 5, maxLength: 5 },
	textarea: { type: 'string', minLength: 1, maxLength: 200 },
	checkbox: { type: 'string' }, // TODO: adjust this
	select: { type: 'string' }, // TODO: adjust this
	disabled_field: { type: 'string' },
	radio_group: { type: 'string' }, // TODO: adjust this
	checkbox_group: { type: 'string' } // TODO: adjust this
};

/**
 * Validation schema for the form: DsrcForm
 */
const schemaDsrcForm = {
	$id: '#/definitions/DsrcForm',
	type: 'object',
	properties: {
		sample_text: { $ref: '#/definitions/text' },
		sample_phone: { $ref: '#/definitions/phone' },
		sample_email: { $ref: '#/definitions/email' },
		sample_password: { $ref: '#/definitions/password' }, // this only validates required length, not password strength
		sample_postcode: { $ref: '#/definitions/postcode' },
		sample_description: { $ref: '#/definitions/textarea' },
		sample_checkbox: { $ref: '#/definitions/checkbox' },
		sample_select: { $ref: '#/definitions/select' },
		sample_disabled_field: { $ref: '#/definitions/disabled_field' },
		sample_radio_group: { $ref: '#/definitions/radio_group' },
		sample_checkbox_group: { $ref: '#/definitions/checkbox_group' }
	},
	required: ['sample_text', 'sample_email', 'sample_password'],
	definitions: schemaFormInputs
};

module.exports = { schemaFormInputs, schemaDsrcForm };
