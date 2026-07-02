import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access administration tab in a project as staff',
  { tag: '@navigation-projet @page-projet-parametres' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      // cy.contains('Administration').click({ force: true })
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/administration'));
    });
  }
);
