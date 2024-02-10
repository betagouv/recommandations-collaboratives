import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, formData) {
	return {
		form: {},
		errors: null,
		ajvValidate: ValidationDsrcForm,
		async init() {
			if (!formData) {
				// TODO: handle errors
			}
			if (formData.errors) {
				// TODO: handle errors
			} else {
				// If no errors: This is a blank form
				const fields = Object.keys(formData);
				fields.forEach((field) => {
					this.form[field] = { ...formData[field], error: null, touched: false };
				});
			}
			this.$nextTick(() => {
				// enable form validation for all submission types (click, keyboard, ...)
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Object.keys(this.errors).length > 0) {
						event.preventDefault();
					}
				});
			});
		},
		validate(event) {
			const fields = Object.keys(this.form);
			const validateMap = {};
			fields.forEach((field) => {
				validateMap[field] = this.form[field].value;
			});
			let valid = this.ajvValidate(validateMap);
			if (!valid) {
				this.errors = this.ajvValidate.errors;
			} else {
				this.errors = null;
			}
		},
		validateInput(event) {
			// TODO: handle errors
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
