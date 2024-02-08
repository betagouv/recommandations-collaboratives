var schemas = {
	text: { type: 'string', minLength: 1, maxLength: 40 },
	phone: { type: 'string', minLength: 8, maxLength: 16 },
	email: { type: 'string', format: 'email' },
	password: { type: 'string', minLength: 8, maxLength: 12 },
	postcode: { type: 'string', minLength: 5, maxLength: 5 },
	textarea: { type: 'string', minLength: 1, maxLength: 200 },
	checkbox: { type: 'string' },
	select: { type: 'string' },
	disabled_field: { type: 'string' },
	radio_group: { type: 'string' },
	checkbox_group: { type: 'string' }
};

const dsrcForm = {
	type: 'object',
	properties: {
		sample_text: { $ref: '#/definitions/string' },
		sample_email: { $ref: '#/definitions/email' },
		sample_password: { $ref: '#/definitions/password' }, // this only validates required length, not passwoerd strength
		sample_postcode: { $ref: '#/definitions/postcode' },
		sample_description: { $ref: '#/definitions/textarea' },
		sample_checkbox: { $ref: '#/definitions/checkbox' },
		sample_select: { $ref: '#/definitions/select' },
		sample_disabled_field: { $ref: '#/definitions/disabled_field' },
		sample_radio_group: { $ref: '#/definitions/radio_group' },
		sample_checkbox_group: { $ref: '#/definitions/checkbox_group' }
	},
	required: ['sample_text', 'sample_email', 'sample_password'],
	definitions: schemas
};

export default { dsrcForm };
