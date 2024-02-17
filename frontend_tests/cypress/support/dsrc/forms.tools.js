/**
 * DSRC - Form Element Tests
 */

const sampleDomElements = {
	TEST_FORM_URL: '/dsrc/',
	FIELD_PREFIX: 'sample_',

	// Sample labels
	LABEL_TEXT: `Nom d'usager`, // TODO:use a selector of type [data-test='test-id']
	LABEL_PHONE: `Téléphone`,
	LABEL_EMAIL: `Courriel`,
	LABEL_PASSWORD: `Mot de passe`,
	LABEL_PASSWORD_CHECKBOX: `Afficher`,
	LABEL_POSTCODE: `Code Postal`,
	LABEL_TEXTAREA: `Description`,
	LABEL_BOOLEAN: `Cochez la case`,
	LABEL_SELECT: ` Liste déroulante`,
	LABEL_DISABLED_INPUT_TEXT: `Champ désactivé`,
	LABEL_RADIO_GROUP: `Boutons radio`,
	LABEL_CHECKBOX_GROUP: `Cases à cocher`,

	// Sample VALID inputs
	VALID_INPUT_TEXT: 'UserTestUI',
	VALID_INPUT_PHONE: '0033122334455', // TODO: use DSFR Pattern
	// this is a fake password to test form validation
	VALID_INPUT_PASSWORD: 'test-test-2est',
	VALID_INPUT_EMAIL: 'user-test-ui@example.com',
	VALID_INPUT_POSTCODE: '79700', // TODO: use DSFR Pattern
	VALID_INPUT_TEXTAREA:
		'This is a sample text with many more characters than the input field can handle'.repeat(10),
	VALID_INPUT_BOOLEAN: 'on',
	VALID_INPUT_SELECT: 'Option 1',
	VALID_INPUT_RADIO_GROUP: 2,
	VALID_INPUT_CHECKBOX_GROUP: 2,

	// Sample INVALID inputs
	INVALID_INPUT_TEXT: ' ', // Invalid if required
	INVALID_INPUT_PHONE: 'abc55', // TODO: use DSFR Pattern
	INVALID_INPUT_PASSWORD: 'test',
	INVALID_INPUT_EMAIL: 'invalid-email',
	INVALID_INPUT_POSTCODE: '79',
	INVALID_INPUT_TEXTAREA: '', // Invalid if required
	INVALID_INPUT_BOOLEAN: 'off', // Invalid if required (Example: accept terms and conditions)
	INVALID_INPUT_SELECT: '', // Invalid if required
	INVALID_INPUT_RADIO_GROUP: 3,
	INVALID_INPUT_CHECKBOX_GROUP: 3
};

class DsrcFormValidator {
	dom;
	fields;
	dataTestPrefix;

	constructor(dataTestPrefix, fields) {
		this.fields = fields;
		this.dataTestPrefix = dataTestPrefix;
		const { fieldSelectors, inputSelectors } = this.getFormSelectors(dataTestPrefix, fields);
		this.dom = { ...sampleDomElements, ...fieldSelectors, ...inputSelectors };
	}

	// Tool functions
	getFieldSelectorKey(inputType) {
		return `FIELD_${inputType.toUpperCase()}`;
	}

	getFieldSelectorValue(dataTestPrefix, inputType) {
		return `[data-test='${dataTestPrefix}${inputType}_field']`;
	}

	getInputSelectorKey(inputType) {
		return `INPUT_${inputType.toUpperCase()}`;
	}

	getInputSelectorValue(dataTestPrefix, inputType, index = null) {
		return index
			? `[data-test='${dataTestPrefix}${inputType}_input-${index}']`
			: `[data-test='${dataTestPrefix}${inputType}_input']`;
	}

	getValidInputValueKey(inputType) {
		return `VALID_INPUT_${inputType.toUpperCase()}`;
	}

	getInvalidInputValueKey(inputType) {
		return `INVALID_INPUT_${inputType.toUpperCase()}`;
	}

	getFormSelectors(dataTestPrefix, fields) {
		const fieldSelectors = {};
		const inputSelectors = {};
		let inputType;
		Object.keys(fields).forEach((index) => {
			inputType = fields[index];
			fieldSelectors[this.getFieldSelectorKey(inputType)] = this.getFieldSelectorValue(
				dataTestPrefix,
				inputType
			);
			inputSelectors[this.getInputSelectorKey(inputType)] = this.getInputSelectorValue(
				dataTestPrefix,
				inputType
			);
		});
		return { fieldSelectors, inputSelectors };
	}

	// Navigation
	navigateToForm() {
		cy.visit(this.dom.TEST_FORM_URL);
	}

	// Verifications
	checkValidity(inputType, isValid = true, fieldSelector, inputSelector) {
		let actualValue;
		let expectedValue;
		if (inputType === 'password') {
			cy.get(inputSelector)
				.invoke('val')
				.then((val) => {
					actualValue = val;
				});
		} else {
			cy.get(inputSelector).then(($input) => {
				actualValue = $input.value;
				if (isValid) {
					expectedValue = this.dom[this.getValidInputValueKey(inputType)];
				} else {
					expectedValue = this.dom[this.getInvalidInputValueKey(inputType)];
				}
			});
		}

		// Check if the input has been entered correctly
		expect(actualValue).to.equal(expectedValue);

		if (isValid) {
			cy.get(`${fieldSelector} [class*="error"]`).should('not.exist');
			cy.get(`${inputSelector}[class*="error"]`).should('not.exist');
		} else {
			cy.get(`${fieldSelector} [class*="error"]`).should('exist');
			cy.get(`${inputSelector}[class*="error"]`).should('exist');
		}
	}

	enterFieldValueAndAssertState(inputType, isValid = true) {
		let fieldSelector = this.dom[this.getFieldSelectorKey(inputType)];
		let inputSelector = this.dom[this.getInputSelectorKey(inputType)];
		switch (inputType) {
			case 'text':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_TEXT);
				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_TEXT : this.dom.INVALID_INPUT_TEXT)
					.blur();

				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);
				break;
			case 'phone':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_PHONE);
				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_PHONE : this.dom.INVALID_INPUT_PHONE)
					.blur();

				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);
				break;
			case 'email':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_EMAIL);
				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_EMAIL : this.dom.INVALID_INPUT_EMAIL)
					.blur();

				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);
				break;
			case 'password':
				// TODO: test password visibility too
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_PASSWORD);

				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_PASSWORD : this.dom.INVALID_INPUT_PASSWORD)
					.blur();
				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);

				break;
			case 'postcode':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_POSTCODE);
				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_POSTCODE : this.dom.INVALID_INPUT_POSTCODE)
					.blur();

				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);
				break;
			case 'textarea':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_TEXTAREA);
				cy.get(inputSelector)
					.type(isValid ? this.dom.VALID_INPUT_TEXTAREA : this.dom.INVALID_INPUT_TEXTAREA)
					.blur();

				this.checkValidity(inputType, isValid, fieldSelector, inputSelector);
				break;
			case 'boolean': // this is a checkbox
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_BOOLEAN);
				cy.get(inputSelector).click().blur();
				cy.get(inputSelector).should('be.checked');

				// TODO: check field and input state on error/valid, test required
				break;
			case 'select':
				cy.get(fieldSelector).should('be.visible').and('contain', this.dom.LABEL_SELECT);

				cy.get(inputSelector).select(
					isValid ? this.dom.VALID_INPUT_SELECT : this.dom.INVALID_INPUT_SELECT
				);
				if (isValid) {
					cy.get(inputSelector).should('have.value', 1);
				} else {
					cy.get(inputSelector).should('have.value', '');
				}
				// TODO: check field and input state on error/valid, test required

				break;

			case 'radio_group':
				cy.get(`${fieldSelector} fieldset`)
					.should('be.visible')
					.and('contain', this.dom.LABEL_RADIO_GROUP);
				if (isValid) {
					inputSelector = this.getInputSelectorValue(
						this.dataTestPrefix,
						inputType,
						this.dom.VALID_INPUT_RADIO_GROUP
					);
				} else {
					inputSelector = this.getInputSelectorValue(
						this.dataTestPrefix,
						inputType,
						this.dom.INVALID_INPUT_RADIO_GROUP
					);
				}
				cy.get(inputSelector).click();
				cy.get(inputSelector).should('be.checked');

				// TODO: check field and input state on error/valid, test required
				break;
			case 'checkbox_group':
				cy.get(`${fieldSelector} fieldset`)
					.should('be.visible')
					.and('contain', this.dom.LABEL_CHECKBOX_GROUP);

				if (isValid) {
					inputSelector = this.getInputSelectorValue(
						this.dataTestPrefix,
						inputType,
						this.dom.VALID_INPUT_CHECKBOX_GROUP
					);
				} else {
					inputSelector = this.getInputSelectorValue(
						this.dataTestPrefix,
						inputType,
						this.dom.INVALID_INPUT_CHECKBOX_GROUP
					);
				}
				cy.get(inputSelector).click();
				cy.get(inputSelector).should('be.checked');

				// TODO: check field and input state on error/valid, test required
				break;
			case 'disabled_field':
				cy.get(fieldSelector).should('contain', this.dom.LABEL_DISABLED_INPUT_TEXT);
				cy.get(inputSelector).should('be.disabled');
				break;
			default:
				break;
		}
	}
}

export default { DsrcFormValidator };
