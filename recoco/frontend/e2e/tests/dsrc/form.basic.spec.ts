import { test } from '../../fixtures';
import { DsrcFormValidator } from '../../helpers/dsrc/forms.tools';

test.describe.skip(
  'DsrcFormValidatorTest',
  { tag: '@dsrc-form-validator' },
  () => {
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
      'checkbox_group',
    ];
    // Create a new instance of DsrcFormValidator using the dataTestPrefix and fields defined in our form
    let dsrcForm: DsrcFormValidator;

    test.beforeEach(async ({ page }) => {
      dsrcForm = new DsrcFormValidator(page, dataTestPrefix, fields);
      await dsrcForm.navigateToForm();
    });

    test('should navigate to the form', async () => {
      await dsrcForm.navigateToForm();
    });

    for (const field of fields) {
      test(`should enter a valid value in "${field}" input and check field state`, async () => {
        await dsrcForm.enterFieldValueAndAssertState(field); // The default value is valid
      });
      test(`should enter an invalid value in "${field}" input and check field state and errors`, async () => {
        await dsrcForm.enterFieldValueAndAssertState(field, false);
      });
    }
  }
);
