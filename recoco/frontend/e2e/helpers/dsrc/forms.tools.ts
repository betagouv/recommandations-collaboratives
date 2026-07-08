/**
 * Port Playwright de cypress/support/dsrc/forms.tools.js — tests des éléments
 * de formulaire DSRC.
 */

import { Page, expect } from '@playwright/test';

const sampleDomElements: Record<string, string | number> = {
  TEST_FORM_URL: '/dsrc/',
  FIELD_PREFIX: 'sample_',

  // Sample labels
  LABEL_TEXT: `Nom d'usager`,
  LABEL_PHONE: `Téléphone`,
  LABEL_EMAIL: `Courriel`,
  LABEL_PASSWORD: `Mot de passe`,
  LABEL_PASSWORD_CHECKBOX: `Afficher`,
  LABEL_POSTCODE: `Code Postal`,
  LABEL_TEXTAREA: `Description`,
  LABEL_BOOLEAN: `Cochez la case`,
  LABEL_SELECT: ` Liste déroulante`,
  LABEL_DISABLED_INPUT_TEXT: `Champ désactivé`,
  LABEL_RADIO_GROUP: `Boutons radio`,
  LABEL_CHECKBOX_GROUP: `Cases à cocher`,

  // Sample VALID inputs
  VALID_INPUT_TEXT: 'UserTestUI',
  VALID_INPUT_PHONE: '0033122334455',
  // this is a fake password to test form validation
  VALID_INPUT_PASSWORD: 'test-test-2est',
  VALID_INPUT_EMAIL: 'user-test-ui@example.com',
  VALID_INPUT_POSTCODE: '79700',
  VALID_INPUT_TEXTAREA:
    'This is a sample text with many more characters than the input field can handle'.repeat(
      10
    ),
  VALID_INPUT_BOOLEAN: 'on',
  VALID_INPUT_SELECT: 'Option 1',
  VALID_INPUT_RADIO_GROUP: 2,
  VALID_INPUT_CHECKBOX_GROUP: 2,

  // Sample INVALID inputs
  INVALID_INPUT_TEXT: ' ', // Invalid if required
  INVALID_INPUT_PHONE: 'abc55',
  INVALID_INPUT_PASSWORD: 'test',
  INVALID_INPUT_EMAIL: 'invalid-email',
  INVALID_INPUT_POSTCODE: '79',
  INVALID_INPUT_TEXTAREA: '', // Invalid if required
  INVALID_INPUT_BOOLEAN: 'off', // Invalid if required
  INVALID_INPUT_SELECT: '', // Invalid if required
  INVALID_INPUT_RADIO_GROUP: 3,
  INVALID_INPUT_CHECKBOX_GROUP: 3,
};

export class DsrcFormValidator {
  dom: Record<string, string | number>;
  fields: string[];
  dataTestPrefix: string;
  page: Page;

  constructor(page: Page, dataTestPrefix: string, fields: string[]) {
    this.page = page;
    this.fields = fields;
    this.dataTestPrefix = dataTestPrefix;
    const { fieldSelectors, inputSelectors } = this.getFormSelectors(
      dataTestPrefix,
      fields
    );
    this.dom = { ...sampleDomElements, ...fieldSelectors, ...inputSelectors };
  }

  // Tool functions
  getFieldSelectorKey(inputType: string) {
    return `FIELD_${inputType.toUpperCase()}`;
  }

  getFieldSelectorValue(dataTestPrefix: string, inputType: string) {
    return `[data-test='${dataTestPrefix}${inputType}_field']`;
  }

  getInputSelectorKey(inputType: string) {
    return `INPUT_${inputType.toUpperCase()}`;
  }

  getInputSelectorValue(
    dataTestPrefix: string,
    inputType: string,
    index: string | number | null = null
  ) {
    return index
      ? `[data-test='${dataTestPrefix}${inputType}_input-${index}']`
      : `[data-test='${dataTestPrefix}${inputType}_input']`;
  }

  getValidInputValueKey(inputType: string) {
    return `VALID_INPUT_${inputType.toUpperCase()}`;
  }

  getInvalidInputValueKey(inputType: string) {
    return `INVALID_INPUT_${inputType.toUpperCase()}`;
  }

  getFormSelectors(dataTestPrefix: string, fields: string[]) {
    const fieldSelectors: Record<string, string> = {};
    const inputSelectors: Record<string, string> = {};
    for (const inputType of fields) {
      fieldSelectors[this.getFieldSelectorKey(inputType)] =
        this.getFieldSelectorValue(dataTestPrefix, inputType);
      inputSelectors[this.getInputSelectorKey(inputType)] =
        this.getInputSelectorValue(dataTestPrefix, inputType);
    }
    return { fieldSelectors, inputSelectors };
  }

  // Navigation
  async navigateToForm() {
    await this.page.goto(String(this.dom.TEST_FORM_URL));
  }

  // Verifications
  async checkValidity(
    inputType: string,
    isValid: boolean,
    fieldSelector: string,
    inputSelector: string
  ) {
    if (inputType !== 'password') {
      const expectedValue = String(
        this.dom[
          isValid
            ? this.getValidInputValueKey(inputType)
            : this.getInvalidInputValueKey(inputType)
        ]
      );
      await expect(this.page.locator(inputSelector)).toHaveValue(
        expectedValue
      );
    }

    const fieldErrors = this.page.locator(`${fieldSelector} [class*="error"]`);
    const inputErrors = this.page.locator(`${inputSelector}[class*="error"]`);
    if (isValid) {
      await expect(fieldErrors).toHaveCount(0);
      await expect(inputErrors).toHaveCount(0);
    } else {
      await expect(fieldErrors.first()).toBeAttached();
      await expect(inputErrors.first()).toBeAttached();
    }
  }

  async enterFieldValueAndAssertState(inputType: string, isValid = true) {
    const fieldSelector = String(this.dom[this.getFieldSelectorKey(inputType)]);
    let inputSelector = String(this.dom[this.getInputSelectorKey(inputType)]);
    const field = this.page.locator(fieldSelector);
    const input = this.page.locator(inputSelector);

    const fillAndBlur = async (value: string) => {
      await input.fill(value);
      await input.blur();
    };

    switch (inputType) {
      case 'text':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_TEXT));
        await fillAndBlur(
          String(
            isValid ? this.dom.VALID_INPUT_TEXT : this.dom.INVALID_INPUT_TEXT
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'phone':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_PHONE));
        await fillAndBlur(
          String(
            isValid ? this.dom.VALID_INPUT_PHONE : this.dom.INVALID_INPUT_PHONE
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'email':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_EMAIL));
        await fillAndBlur(
          String(
            isValid ? this.dom.VALID_INPUT_EMAIL : this.dom.INVALID_INPUT_EMAIL
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'password':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_PASSWORD));
        await fillAndBlur(
          String(
            isValid
              ? this.dom.VALID_INPUT_PASSWORD
              : this.dom.INVALID_INPUT_PASSWORD
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'postcode':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_POSTCODE));
        await fillAndBlur(
          String(
            isValid
              ? this.dom.VALID_INPUT_POSTCODE
              : this.dom.INVALID_INPUT_POSTCODE
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'textarea':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_TEXTAREA));
        await fillAndBlur(
          String(
            isValid
              ? this.dom.VALID_INPUT_TEXTAREA
              : this.dom.INVALID_INPUT_TEXTAREA
          )
        );
        await this.checkValidity(
          inputType,
          isValid,
          fieldSelector,
          inputSelector
        );
        break;
      case 'boolean': // this is a checkbox
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_BOOLEAN));
        await input.click();
        await expect(input).toBeChecked();
        break;
      case 'select':
        await expect(field).toBeVisible();
        await expect(field).toContainText(String(this.dom.LABEL_SELECT));
        await input.selectOption({
          label: String(
            isValid
              ? this.dom.VALID_INPUT_SELECT
              : this.dom.INVALID_INPUT_SELECT
          ),
        });
        await expect(input).toHaveValue(isValid ? '1' : '');
        break;
      case 'radio_group': {
        const fieldset = this.page.locator(`${fieldSelector} fieldset`);
        await expect(fieldset).toBeVisible();
        await expect(fieldset).toContainText(
          String(this.dom.LABEL_RADIO_GROUP)
        );
        inputSelector = this.getInputSelectorValue(
          this.dataTestPrefix,
          inputType,
          isValid
            ? (this.dom.VALID_INPUT_RADIO_GROUP as number)
            : (this.dom.INVALID_INPUT_RADIO_GROUP as number)
        );
        const radio = this.page.locator(inputSelector);
        await radio.click();
        await expect(radio).toBeChecked();
        break;
      }
      case 'checkbox_group': {
        const fieldset = this.page.locator(`${fieldSelector} fieldset`);
        await expect(fieldset).toBeVisible();
        await expect(fieldset).toContainText(
          String(this.dom.LABEL_CHECKBOX_GROUP)
        );
        inputSelector = this.getInputSelectorValue(
          this.dataTestPrefix,
          inputType,
          isValid
            ? (this.dom.VALID_INPUT_CHECKBOX_GROUP as number)
            : (this.dom.INVALID_INPUT_CHECKBOX_GROUP as number)
        );
        const checkbox = this.page.locator(inputSelector);
        await checkbox.click();
        await expect(checkbox).toBeChecked();
        break;
      }
      case 'disabled_field':
        await expect(field).toContainText(
          String(this.dom.LABEL_DISABLED_INPUT_TEXT)
        );
        await expect(input).toBeDisabled();
        break;
      default:
        break;
    }
  }
}
