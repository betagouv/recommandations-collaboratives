import { expect, test } from '@playwright/test';

import { authFile } from '../../../../helpers/users';

test.describe.configure({ mode: 'serial' });

test.describe(
  'I can go to CRM and toggle project impact tag',
  { tag: '@bouton-raccourci-crm-staff' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test.beforeEach(async ({ page }) => {
      await page.goto(`/crm/project/2`);
    });

    test('toggle on an impact tag', async ({ page }) => {
      await expect(
        page.getByText('A nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
      await expect(
        page.getByText('Another nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
      await page.getByText('A nice tag').first().click();
      await expect(
        page.getByText('A nice tag').first().locator('..').locator('input')
      ).toBeChecked();
      await expect(
        page.getByText('Another nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
    });

    // Titre dédoublonné : le 2e « toggle on an impact tag » Cypress désactive le tag
    test('toggle off an impact tag', async ({ page }) => {
      await expect(
        page.getByText('A nice tag').first().locator('..').locator('input')
      ).toBeChecked();
      await expect(
        page.getByText('Another nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
      await page.getByText('A nice tag').first().click();
      await expect(
        page.getByText('A nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
      await expect(
        page.getByText('Another nice tag').first().locator('..').locator('input')
      ).not.toBeChecked();
    });
  }
);
