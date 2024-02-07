import dsrcForm from '../../support/dsrc/forms.tools.js';

describe('DsrcForm', () => {
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
	beforeEach(() => {
		// Create a new instance of DsrcForm before each test
		dsrcForm.navigateToForm();
	});

	it('should navigate to the form', () => {
		// Test the navigateToForm method
		dsrcForm.navigateToForm();
		// Add your assertions here
	});

	it('should check field state', () => {});

	it('should enter field value and display errors ir input is invalid', () => {
		fields.forEach((field) => {
			dsrcForm.enterFieldValueAndAssertState(field);
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
