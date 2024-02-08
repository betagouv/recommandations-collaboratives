import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import formSchemas from './forms.schema';

const ajv = new Ajv();
addFormats(ajv);

function DsrcForm(formId, formData) {
	return {
		formData: {},
		errors: {},
		schema: formSchemas.dsrcForm,
		init() {
			console.log('"Alpine.js component is initialized"', valid);
			// Initialize AJV and compile your schema here
			this.formData = formData;
			validate = Ajv.compile(schema);
			this.$nextTick(() => {
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Object.keys(this.errors).length > 0) {
						event.preventDefault();
					}
				});
			});
			// Initialize
		},
		validate() {
			let valid = validate(this.formData);
			console.log('valid', valid);
			if (!valid) {
				this.errors = validate.errors;
			}
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
