import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, formData) {
	return {
		form: {},
		errors: [],
		ajvValidate: ValidationDsrcForm,
		async init() {
			if (!formData) {
				// TODO: handle errors
				console.error('Error fetching form data');
			}
			if (formData.errors) {
				// TODO: handle errors
			} else {
				// If no errors: This is a blank form
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
					}
				});
			});
		},
		validate(event) {
			let valid = this.ajvValidate(this.form);
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
		validateInput(event) {
			const field = event.target.name;
			this.validate();
			this.form[field].errors = this.getFieldErrors(field);
		},
		touchInput(event) {
			this.form[event.target.name].touched = true;
		},
		changeInput(event) {
			this.form[event.target.name].changed = true;
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
