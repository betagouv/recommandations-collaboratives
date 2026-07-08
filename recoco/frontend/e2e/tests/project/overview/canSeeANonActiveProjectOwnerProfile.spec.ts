import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to overview tab',
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    let currentProject = projects[9];

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
    });

    test('show the profile of a non active project owner with the correct class', async ({
      page,
    }) => {
      await expect(
        page.locator('[data-test-id="project-owner-name-details"]')
      ).toHaveClass(/inactive-status/);
    });

    test('show the tooltip of a non active user with the date of last connection', async ({
      page,
    }) => {
      await page
        .locator(
          '[data-test-id="project-information-card-context"] [data-test-id="button-open-tooltip-user-card"]'
        )
        .click({ force: true });
      const introText = await page
        .locator(
          '[data-test-id="project-information-card-context"] [data-test-id="user-card-intro"]'
        )
        .innerText();
      expect(introText.length).toBeGreaterThan(0);
      await expect(
        page.locator('[data-test-id="deactivated-user-details"]').first()
      ).toBeAttached();
    });

    test('show an anonymous user card if the user does not exist', async ({
      page,
    }) => {
      currentProject = projects[13]; // submitted_by: deleted.user@test.fr

      // First: delete the user that submitted the project to test
      await page.goto('/nimda/auth/user/');
      await page
        .getByText('deleted.user@test.fr')
        .first()
        .click({ force: true });
      await page.locator('.deletelink').click({ force: true });
      await expect(
        page.getByText('deleted.user@test.fr').first()
      ).toBeAttached();
      await page.locator('input[type=submit]').click({ force: true });

      // Second: Visit the project to test and check the display of the deleted user card
      await page.goto(`/project/${currentProject.pk}/presentation`);
      // Le bouton est hors viewport ; Cypress dispatchait le clic sur l'élément
      // (force:true), on reproduit avec dispatchEvent.
      await page
        .locator(
          '[data-test-id="project-information-card-context"] [data-test-id="button-open-tooltip-user-card"]'
        )
        .dispatchEvent('click');
      await expect(
        page.locator(
          '[data-test-id="project-information-card-context"] [data-test-id="user-card-intro"]'
        )
      ).toHaveCount(0);
      await expect(
        page.locator('[data-test-id="deleted-user-details"]').first()
      ).toBeAttached();
    });
  }
);
