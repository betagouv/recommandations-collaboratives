import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can assign some deparments when I create a resource',
  { tag: '@acces-ressources' },
  () => {
    test('goes to create a resource and assign 2 deparments', async ({
      page,
    }) => {
      await page.goto('/ressource/create/');

      const title = page.locator('#id_title');
      await title.fill('Ressource de test');
      await expect(title).toHaveValue('Ressource de test');

      const subtitle = page.locator('#id_subtitle');
      await subtitle.fill('Soustitre de la ressource de test');
      await expect(subtitle).toHaveValue('Soustitre de la ressource de test');

      const summary = page.locator('#id_summary');
      await summary.fill('résumé de la ressource de test');
      await expect(summary).toHaveValue('résumé de la ressource de test');

      const tags = page.locator('#id_tags');
      await tags.fill('etiquette1');
      await expect(tags).toHaveValue('etiquette1');

      await page.locator('#select-list-input').click();
      await page
        .locator('label')
        .filter({ hasText: 'Département de test' })
        .first()
        .click({ force: true });
      await page
        .locator('label')
        .filter({ hasText: 'Département de test numéro 2' })
        .click({ force: true });

      await page.locator('#id_expires_on').fill('2022-12-20');

      await page.locator('.ProseMirror p').first().click();
      await page.keyboard.type('text');

      await page
        .locator('[data-test-id="publish-resource-btn"]')
        .click({ force: true });

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(page.getByText('Ressource de test').first()).toBeVisible();
      await expect(
        page.getByText('résumé de la ressource de test').first()
      ).toBeVisible();

      await expect(
        page
          .getByText(
            'Cette ressource est disponible dans les départements suivants :'
          )
          .first()
      ).toBeVisible();
      await expect(
        page.getByText('Département de test').first()
      ).toBeVisible();
      await expect(
        page.getByText('Département de test numéro 2').first()
      ).toBeVisible();
    });
  }
);
