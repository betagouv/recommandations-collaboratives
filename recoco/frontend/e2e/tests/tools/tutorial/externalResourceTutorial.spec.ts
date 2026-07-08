import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.use({ storageState: authFile('conseiller1') });

// TODO Réécrire : create-task-button n'est plus accessible depuis /actions (page redirigée)
test.describe.skip(
  'I can follow the external resource tutorial',
  { tag: '@tutoriel-ressource-externe' },
  () => {
    test('displays the launcher tutorial on the external resource', async ({
      page,
    }) => {
      await page.goto('/project/27/actions');
      await page.locator("[data-test-id='create-task-button']").click();
      await page
        .locator("[data-cy='radio-push-reco-external-resource']")
        .check({ force: true });
      await expect(
        page.locator('[data-test-id="tutorial-project-launcher"]').first()
      ).toBeAttached();
    });
  }
);
