import { DsrcForm } from '../../support/dsrc/forms.tools.js';

describe('DsrcFormTest', () => {
	// The prefix used in data-test selectors: the selectors are generated in the `forms.py` during form initialization, and are rendered in the template files
	const dataTestPrefix = 'dsrc_test_sample_';
	// The fields to test: these are the names of the fields of the form, as declared in the `forms.py` file, without the `sample_` prefix
	const fields = [
		'text',
		'phone',
		'email',
		'password',
		'postcode',
		'description',
		'boolean',
		'select',
		'disabled_field',
		'radio_group',
		'checkbox_group'
	];
	// Create a new instance of DsrcForm using the dataTestPrefix and fields defined in our form
	const dsrcForm = new DsrcForm(dataTestPrefix, fields);

	beforeEach(() => {
		// Create a new instance of DsrcForm before each test
		dsrcForm.navigateToForm();
	});

	it('should navigate to the form', () => {
		// Test the navigateToForm method
		dsrcForm.navigateToForm();
		// Add your assertions here
	});

	it('should enter an valid input and check field state', () => {
		fields.forEach((field) => {
			dsrcForm.enterFieldValueAndAssertState(field);
			// Add your assertions here
		});
	});

	it('should enter an invalid input, check field state and display errors', () => {
		fields.forEach((field) => {
			dsrcForm.enterFieldValueAndAssertState(field, false);
			// Add your assertions here
		});
	});
	// it('should save the form', () => {
	// 	// Test the saveDsrcForm method
	// 	dsrcForm.saveDsrcForm();
	// 	// Add your assertions here
	// });

	// Add more test cases for other methods
});
