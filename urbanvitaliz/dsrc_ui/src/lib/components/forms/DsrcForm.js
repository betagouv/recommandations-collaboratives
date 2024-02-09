import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, formData) {
	return {
		formData: {},
		errors: {},
		ajvValidate: ValidationDsrcForm,
		init() {
			// Initialize AJV and compile your schema here
			this.formData = formData ?? {
				sample_text: '',
				sample_email: '',
				sample_password: '',
				sample_postcode: '',
				sample_description: '',
				sample_checkbox: 'off',
				sample_select: '',
				sample_disabled_field: '',
				sample_radio_group: '',
				sample_checkbox_group: ''
			};
			this.$nextTick(() => {
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Object.keys(this.errors).length > 0) {
						event.preventDefault();
					}
				});
			});
			console.log('"DsrcForm.js component is initialized"');
		},
		validate() {
			let valid = this.ajvValidate(this.formData);
			console.log('valid', valid);
			if (!valid) {
				this.errors = validate.errors;
			}
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
