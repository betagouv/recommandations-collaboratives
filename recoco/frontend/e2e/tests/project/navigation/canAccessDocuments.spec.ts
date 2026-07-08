import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';

const currentProject = projects[1];

test.describe(
  'I can access documents tab in a project',
  { tag: '@navigation-projet @page-projet-fichier' },
  () => {
    test('goes to the documents page of my project as a member', async ({
      loginAs,
    }) => {
      const page = await loginAs('collectivité1');
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator('[data-test-id="project-navigation-documents"]')
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/documents'));
    });

    test('goes to the documents page of my project as an advisor', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator('[data-test-id="project-navigation-documents"]')
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/documents'));
    });
  }
);
