/**
 * This file contains the JSON schema for the form fields.
 * The schemas are used by he Ajv validator to validate the form fields.
 */
const schemaFormInputs = {
	text: { type: 'string', minLength: 1, maxLength: 40 },
	phone: { type: 'string', minLength: 8, maxLength: 16 },
	email: { type: 'string', format: 'email' },
	password: { type: 'string', format: 'password', minLength: 8, maxLength: 12 },
	postcode: { type: 'string', minLength: 5, maxLength: 5 },
	textarea: { type: 'string', minLength: 1, maxLength: 200 },
	checkbox: { type: 'string' },
	select: { type: 'string' },
	disabled_field: { type: 'string' },
	radio_group: { type: 'string' },
	checkbox_group: { type: 'string' }
};

/**
 * The validation schema for the form: DsrcForm
 *
 * To use the schema:
 * - compile the schema into a validation function using the `generateValidator` function defined in `src/ext/ajv.validator.js`.
 * To see how the validation is used in the form, see the `DsrcForm.js` file.
 *
 * AJV Doc: https://ajv.js.org/guide/getting-started.htmlhttps://ajv.js.org/guide/getting-started.html
 */
const schemaDsrcForm = {
	$id: '#/definitions/DsrcForm',
	type: 'object',
	properties: {
		sample_text: { $ref: '#/definitions/text' },
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

module.exports = { schemaDsrcForm };
