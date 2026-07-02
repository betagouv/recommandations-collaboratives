import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can assign new deparments when I edit a resource',
  { tag: '@acces-ressources' },
  () => {
    test('goes to edit a resource and assign a new deparment', async ({
      page,
    }) => {
      await page.goto('/ressource/1/');
      await page.locator('[data-test-id="edit-resource"]').click();

      await page
        .locator('[data-test-id="open-multiselect"]')
        .click({ force: true });

      // Checkbox masquée par design (classe d-none) : équivalent du force:true
      await page.locator('[id="department-1"]').dispatchEvent('click');
      await page
        .locator('[data-test-id="publish-resource-btn"]')
        .click({ force: true });

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(
        page.getByText('Département de test numéro 2').first()
      ).toBeVisible();
    });
  }
);
