import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, formData) {
	return {
		formData: {},
		errors: {},
		ajvValidate: {},
		init() {
			// Initialize AJV and compile your schema here
			this.ajvValidate = ValidationDsrcForm['#/definitions/DsrcForm'];
			this.formData = formData;
			this.$nextTick(() => {
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Object.keys(this.errors).length > 0) {
						event.preventDefault();
					}
				});
			});
			console.log('"Alpine.js component is initialized"');
		},
		validate() {
			let valid = ajvValidate(this.formData);
			console.log('valid', valid);
			if (!valid) {
				this.errors = validate.errors;
			}
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
