/************************************************************************************
 * This file contains JSON schema for form validation with Ajv
 *
 * AJV Doc on Combining Schemas: https://ajv.js.org/guide/combining-schemas.html
 ************************************************************************************/

function generateMaxLengthErrorMessage(maxLength) {
	return `${maxLength} caractère${maxLength > 1 ? 's' : ''}  maximum`;
}

function generateMinLengthErrorMessage(minLength) {
	return `${minLength} caractère${minLength > 1 ? 's' : ''} minimum`;
}

/**
 * Password schema
 * Note: This schema only validates the required length and character classes. It does not guarantee password strength.
 */

/**
 * Common Schemas for form inputs.
 */
const schemaFormInputs = {
	text: {
		allOf: [
			{
				type: 'string',
				minLength: 3,
				errorMessage: generateMinLengthErrorMessage(3)
			},
			{
				type: 'string',
				maxLength: 100,
				errorMessage: generateMaxLengthErrorMessage(100)
			}
		]
	},
	phone: {
		type: 'string',
		pattern: '[\\+0-9]{10,14}',
		errorMessage: {
			errorMessage: 'Veuillez rentrer un téléphone valide'
		}
	},
	email: {
		type: 'string',
		format: 'email',
		errorMessage: {
			format: 'Veuillez rentrer une adresse email valide'
		}
	},
	password: {
		// TODO : adapt for true password validation
		allOf: [
			{
				type: 'string',
				format: 'password',
				minLength: 12,
				errorMessage: generateMinLengthErrorMessage(12)
			},
			{
				type: 'string',
				pattern: '[$-+!?*&%~_@#]{1}',
				errorMessage: '1 caractère spécial minimum'
			},
			{
				type: 'string',
				pattern: '[0-9]{1}',
				errorMessage: '1 chiffre minimum'
			}
		]
	},
	postcode: {
		// TODO : adapt for true postcode validation
		allOf: [
			{
				type: 'string',
				minLength: 5,
				errorMessage: generateMinLengthErrorMessage(5)
			},
			{
				type: 'string',
				maxLength: 5,
				errorMessage: generateMaxLengthErrorMessage(5)
			}
		]
	},
	textarea: {
		type: 'string',
		maxLength: 200,
		errorMessage: {
			maxLength: generateMaxLengthErrorMessage(200)
		}
	},
	checkbox: { type: 'string' }, // adjust this as necessary
	select: { type: 'string' }, // adjust this as necessary
	disabled_field: { type: 'string' }, // adjust this as necessary
	radio_group: { type: 'string' }, // adjust this as necessary
	checkbox_group: { type: 'string' } // adjust this as necessary
};

/**
 * Validation schema for the form: DsrcForm
 */
const schemaDsrcForm = {
	$id: '#/definitions/DsrcForm',
	type: 'object',
	properties: {
		sample_name: { $ref: '#/definitions/text' },
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
	required: ['sample_name', 'sample_email', 'sample_password'],
	definitions: schemaFormInputs
};

module.exports = { schemaFormInputs, schemaDsrcForm };
