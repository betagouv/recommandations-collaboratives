import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to a project and select my role on it',
  { tag: '@changement-role-projet' },
  () => {
    test.use({ storageState: authFile('jean') });

    test('can become observer, advisor or quit project as regional advisor', async ({
      page,
    }) => {
      await page.goto('/project/2');

      const banner = page.locator(
        '[data-test-id="select-observer-or-advisor-button"]'
      );
      // Le clic d'ouverture peut partir avant l'hydratation Alpine : on
      // re-clique jusqu'à ce que le sélecteur de rôle apparaisse, et les
      // boutons du menu (clippés) reçoivent un dispatchEvent (force Cypress).
      const quitRole = page.locator('[data-test-id="button-quit-role"]').first();
      await expect(async () => {
        await banner.click({ force: true });
        await expect(quitRole).toBeAttached({ timeout: 2_000 });
      }).toPass({ timeout: 15_000 });
      await quitRole.dispatchEvent('click');
      await expect(banner).toContainText('Rejoindre');

      const becomeAdvisor = page
        .locator('[data-test-id="button-become-advisor"]')
        .first();
      await expect(async () => {
        await banner.click({ force: true });
        await expect(becomeAdvisor).toBeAttached({ timeout: 2_000 });
      }).toPass({ timeout: 15_000 });
      await becomeAdvisor.dispatchEvent('click');
      await expect(banner).toContainText('Quitter');
    });
  }
);
