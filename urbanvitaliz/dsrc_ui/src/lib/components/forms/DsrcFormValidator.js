import Alpine from 'alpinejs';
import * as validations from '../../../ext/ajv.validations.default';

/**
 * Use this Alpine component to provide frontend validation capabilities to a form rendered by the server.
 * @param {string} formId The id of the <form> element
 * @param {Object} formData The serialized form data from the server, defined in `forms.py` and serialized in `views.py`
 * @param {string} validationFunctionName The name of the AJV validation function to use. It should be generated into `ajv.validations.default.js` by the script `build:ajv` (`DsrcFormValidationFunction` is the default validation function for DsrcExampleForm). To Change the default validation function, add the schema for your form to `ajv.schema.forms.cjs` and run `npm run build:ajv`
 * @returns an Alpine component object containing the form data and methods to validate and handle form submission
 */
export const DsrcFormValidator = (
	formId,
	formData,
	validationFunctionName = 'DsrcFormValidationFunction'
) => {
	return {
		form: {},
		errors: [],
		ajvValidate: validations[validationFunctionName],
		async init() {
			if (!formData) {
				// We shouldn't reach this state: the data should be available, or the server should have returned an error before reaching this point and the form should not have been rendered
				console.error('Error fetching form data');
			}
			if (formData.errors) {
				// We shouldn't reach this state: AJV validation should have prevented form submission
				console.error('Error validating form data with AJV');
			} else {
				// There are no errors: This is a blank form
				const fields = Object.keys(formData);
				fields.forEach((field) => {
					this.form[field] = {
						message_group: {
							messages: [],
						},
						errors: [],
						touched: false,

						changed: false,
						...formData[field]

					};
				});
			}
			this.$nextTick(() => {
				// enable form validation for all submission types (click, keyboard, ...)
				document
					.getElementById(formId)
					.addEventListener('submit', (event) => {
						this.validate();
						if (
							Array.isArray(this.errors) &&
							this.errors.length > 0
						) {
							event.preventDefault();
							// Set the focus on the first field with an error
							const firstErrorField =
								this.errors[0].instancePath.substring(1);
							this.form[firstErrorField].is_valid = false;
							this.form[firstErrorField].errors =
								this.getFieldErrors(firstErrorField);
							this.form[firstErrorField].valid_class = 'error';
							this.$refs[firstErrorField].focus();
						}
					});
			});
			// Disable browser validation as we are using our own
			document.getElementById(formId).setAttribute('novalidate', '');
			// Let the server know that JS is enabled
			document.getElementById(`${formId}_js_enabled`).value = 'true';
		},
		validate(event) {
			// debug
			const fields = Object.keys(this.form);
			const validateMap = {};
			fields.forEach((field) => {
				validateMap[field] = this.form[field].value;
			});
			let valid = this.ajvValidate(validateMap);
			if (!valid) {
				this.errors = this.ajvValidate.errors;
			} else {
				this.errors = [];
			}
		},
		getFieldErrors(fieldName) {
			const errors = this.errors.filter(
				(error) => error.instancePath.substring(1) === fieldName
			);
			return errors.map((error) => error.message);
		},
		setFieldMessages(fieldName) {
			const field = this.form[fieldName];
			if (!field.message_group || !field.message_group.messages) {
				field.message_group = { help_text: '', messages: [] };
			}
			let filteredMessages = [];
			if (
				field.message_group.messages.length === 0 &&
				field.errors.length > 0
			) {
				filteredMessages = (field.errors || []).map((error) => ({
					text: error,
					type: 'error',
				}));
			} else {
				// If the field has a message_group set by the server: match local messages with error messages and set the message type accordingly
				filteredMessages = field.message_group.messages.reduce((updatedMessages, message) => {
					if (field.errors.includes(message.text)) {
						message.type = 'error';
					} else {
						message.type = 'valid';
					}
					return [...updatedMessages, message];
				}, []);
			}
			field.message_group.messages = filteredMessages;
		},
		fieldHasError(fieldName) {
			const field = this.form[fieldName];
			return field.touched === true && field.errors.length > 0;
		},
		validateInput(event) {
			const fieldName = event.target.name;
			this.validate();
			this.form[fieldName].errors = this.getFieldErrors(fieldName);
			if (
				this.form[fieldName].is_valid === false &&
				this.form[fieldName].errors.length === 0
			) {
				this.form[fieldName].is_valid = true;
				this.form[fieldName].valid_class = 'valid';
			} else if (this.form[fieldName].errors.length > 0) {
				this.form[fieldName].is_valid = false;
				this.form[fieldName].valid_class = 'error';
			}
			this.setFieldMessages(fieldName);
		},
		touchInput(event) {
			const field = event.target.name;
			this.form[field].touched = true;
		},
		changeInput(event) {
			const field = event.target.name;
			this.form[field].changed = true;
			// validate the field when it changes: remove this if you want to validate the form only on `blur` or `submit` events
			// Use a debounce mechanism for slow/complex/async validations (e.g. API calls)
			this.validateInput(event);
		},
	};
};

Alpine.data('DsrcFormValidator', DsrcFormValidator);

export default DsrcFormValidator;
