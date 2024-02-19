import { DsrcFormValidator } from '../../support/dsrc/forms.tools.js';

describe('DsrcFormValidatorTest', () => {
	// The prefix used in data-test selectors: the selectors are generated in the `forms.py` during form initialization, and are rendered in the template files
	const fieldPrefix = 'sample_';
	const dataTestPrefix = `dsrc_test_${fieldPrefix}`;
	// The fields to test = the input types of the fields stripped of the `sample_` prefix used in the `forms.py` file,
	const fields = [
		'name',
		'phone',
		'email',
		'password',
		'postcode',
		'description',
		'checkbox',
		'select',
		'disabled_field',
		'radio_group',
		'checkbox_group'
	];
	// Create a new instance of DsrcFormValidator using the dataTestPrefix and fields defined in our form
	const dsrcForm = new DsrcFormValidator(dataTestPrefix, fields);

	beforeEach(() => {
		dsrcForm.navigateToForm();
	});

	it('should navigate to the form', () => {
		dsrcForm.navigateToForm();
	});

	fields.forEach((field) => {
		it(`should enter a valid value in "${field}" input and check field state`, () => {
			dsrcForm.enterFieldValueAndAssertState(field); // The default value is valid
		});
		it(`should enter an invalid value in "${field}" input and check field state and errors`, () => {
			dsrcForm.enterFieldValueAndAssertState(field, false);
		});
	});
});
