import { expect, test } from '../../../fixtures';

import projects from '../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'Private files section visibility on documents page',
  { tag: '@page-projet-fichier' },
  () => {
    test('advisor can see the private files section', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/${currentProject.pk}/documents`);
      await expect(
        page.locator('[data-test-id="private-files-section"]').first()
      ).toBeAttached();
    });

    test('collectivité cannot see the private files section', async ({
      loginAs,
    }) => {
      const page = await loginAs('collectivité1');
      await page.goto(`/project/${currentProject.pk}/documents`);
      await expect(
        page.locator('[data-test-id="private-files-section"]')
      ).toHaveCount(0);
    });
  }
);
