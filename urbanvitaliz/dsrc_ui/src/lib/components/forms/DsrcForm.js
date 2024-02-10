import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, dataUrl) {
	return {
		form: {},
		errors: {},
		ajvValidate: ValidationDsrcForm,
		async init() {
			try {
				const response = await fetch(dataUrl);
				if (response.ok) {
					this.form = await response.json();
				}
				this.$nextTick(() => {
					document.getElementById(formId).addEventListener('submit', (event) => {
						this.validate();
						if (Object.keys(this.errors).length > 0) {
							event.preventDefault();
						}
					});
				});
			} catch (error) {
				// console.error('Error fetching form data', error);
			}
		},
		validate() {
			let valid = this.ajvValidate(this.form);
			if (!valid) {
				this.errors = this.ajvValidate.errors;
			}
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
