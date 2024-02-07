/**
 * DSRC - Form Element Tests
 */

const domElements = {
	TEST_FORM_URL: '/dsrc/',
	// Sample fields
	SAMPLE_FIELD_TEXT: '[name="sample_text"]', // TODO:use a selector of type [data-test='test-id']
	SAMPLE_FIELD_PHONE: '[name="sample_phone"]',
	SAMPLE_FIELD_EMAIL: '[name="sample_email"]',
	SAMPLE_FIELD_PASSWORD: '[name="sample_password"]',
	SAMPLE_FIELD_POSTCODE: '[name="sample_postcode"]',
	SAMPLE_FIELD_TEXTAREA: '[name="sample_description"]',
	SAMPLE_FIELD_BOOLEAN: '[name="sample_boolean"]',
	SAMPLE_FIELD_SELECT: '[name="sample_select"]',
	SAMPLE_FIELD_DISABLED_INPUT_TEXT: '[name="sample_disabled_field"]',
	SAMPLE_FIELD_RADIO_GROUP: '[name="sample_radio_group"',
	SAMPLE_FIELD_CHECKBOX_GROUP: '[name="sample_checkbox_group"]',

	// Sample VALID inputs
	VALID_INPUT_TEXT: 'This is a sample text',
	VALID_INPUT_PHONE: '0033122334455', // TODO: use DSFR Pattern
	VALID_INPUT_PASSWORD: '*Do-487-NoT-$use+THIS-asIS', // "Secure" password example, don't use it outside test environment
	VALID_INPUT_EMAIL: 'julie@example.com',
	VALID_INPUT_POSTCODE: '79700', // TODO: use DSFR Pattern
	VALID_INPUT_TEXTAREA:
		'This is a sample text with many more characters than the input field can handle'.repeat(10),
	VALID_INPUT_BOOLEAN: true,
	VALID_INPUT_SELECT: 'Option 1',
	VALID_INPUT_RADIO: 2,
	VALID_INPUT_CHECKBOX: 1,

	// Sample INVALID inputs
	INVALID_INPUT_TEXT: 'This is a sample text',
	INVALID_INPUT_PHONE: 'abc55', // TODO: use DSFR Pattern
	INVALID_INPUT_PASSWORD: 'unsafe-Passw0rd', // insecure password example
	INVALID_INPUT_EMAIL: 'julieexample.com',
	INVALID_INPUT_POSTCODE: '79',
	INVALID_INPUT_TEXTAREA: '', // Invalid if required
	INVALID_INPUT_BOOLEAN: true,
	INVALID_INPUT_SELECT: 'Option 1',
	INVALID_INPUT_RADIO: 3,
	INVALID_INPUT_CHECKBOX: 3
};

class DsrcForm {
	dom;

	constructor(dom) {
		this.dom = dom;
	}

	// Navigation
	navigateToForm() {
		cy.visit(this.dom.TEST_FORM_URL);
	}

	// Verifications

	checkValidity(inputType, isValid = true) {
		// Check if the input is valid
		if (isValid) {
			expect(inputType[0].checkValidity()).to.equal(true);
		} else {
			expect(inputType[0].checkValidity()).to.equal(false);
		}
	}

	enterFieldValueAndAssertState(inputType, isValid = true) {
		switch (inputType) {
			case 'text':
				cy.get(this.dom.SAMPLE_FIELD_TEXT)
					.type(isValid ? this.dom.VALID_INPUT_TEXT : this.dom.INVALID_INPUT_TEXT)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'phone':
				cy.get(this.dom.SAMPLE_FIELD_PHONE)
					.type(isValid ? this.dom.VALID_INPUT_PHONE : this.dom.INVALID_INPUT_PHONE)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'email':
				cy.get(this.dom.SAMPLE_FIELD_EMAIL)
					.type(isValid ? this.dom.VALID_INPUT_EMAIL : this.dom.INVALID_INPUT_EMAIL)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'password':
				cy.get(this.dom.SAMPLE_FIELD_PASSWORD)
					.type(isValid ? this.dom.VALID_INPUT_PASSWORD : this.dom.INVALID_INPUT_PASSWORD)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'postcode':
				cy.get(this.dom.SAMPLE_FIELD_POSTCODE)
					.type(isValid ? this.dom.VALID_INPUT_POSTCODE : this.dom.INVALID_INPUT_POSTCODE)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'textarea':
				cy.get(this.dom.SAMPLE_FIELD_TEXTAREA)
					.type(isValid ? this.dom.VALID_INPUT_TEXTAREA : this.dom.INVALID_INPUT_TEXTAREA)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'boolean': // this is a checkbox
				cy.get(this.dom.SAMPLE_FIELD_BOOLEAN)
					.click()
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'select':
				cy.get(this.dom.SAMPLE_FIELD_SELECT)
					.select(this.dom.VALID_INPUT_SELECT)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'radio_group':
				cy.get(this.dom.SAMPLE_FIELD_RADIO_GROUP)
					.check(this.dom.VALID_INPUT_RADIO)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			case 'checkbox_group':
				cy.get(this.dom.SAMPLE_FIELD_CHECKBOX_GROUP)
					.check(this.dom.VALID_INPUT_CHECKBOX)
					.then(($input) => {
						checkValidity($input, isValid);
					});
				break;
			default:
				break;
		}
	}
}

const dsrcForm = new DsrcForm(domElements);

export default dsrcForm;
