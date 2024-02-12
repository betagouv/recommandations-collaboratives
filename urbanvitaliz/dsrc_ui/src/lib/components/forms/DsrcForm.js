import Alpine from 'alpinejs';
import * as validations from '../../../ext/ajv.validations.default';

function DsrcForm(formId, formData, validationFunctionName = 'ValidationDsrcForm') {
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
					this.form[field] = { ...formData[field], errors: [], touched: false };
				});
			}
			this.$nextTick(() => {
				// enable form validation for all submission types (click, keyboard, ...)
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Array.isArray(this.errors) && this.errors.length > 0) {
						event.preventDefault();
						// Set the focus on the first field with an error
						const firstErrorField = this.errors[0].instancePath.substring(1);
						this.form[firstErrorField].is_valid = false;
						this.form[firstErrorField].errors = this.getFieldErrors(firstErrorField);
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
			const errors = this.errors.filter((error) => error.instancePath.substring(1) === fieldName);
			return errors.map((error) => error.message);
		},
		setFieldMessages(fieldName) {
			const field = this.form[fieldName];
			let filteredMessages = [];

			if (!field.message_group) {
				// If the field does't have a message_group set by the server: create a message_group and add the errors to it
				field.message_group = {};
				if (field.errors.length > 0) {
					filteredMessages = (field.errors || []).map((error) => ({ text: error, type: 'error' }));
				}
			} else {
				// If the field has a message_group set by the server: match messages with error messages and set the message type accordingly
				filteredMessages = field.message_group.messages.map((message) => {
					if (field.errors.includes(message.text)) {
						return { text: message.text, type: 'error' };
					}
					return { text: message.text, type: 'valid' };
				});
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
			if (this.form[fieldName].is_valid === false && this.form[fieldName].errors.length === 0) {
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
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
