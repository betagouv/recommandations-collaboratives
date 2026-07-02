import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.describe.configure({ mode: 'serial' });

test.describe(
  'I can go to the dashboard and see the pending demand for advising, and manage one',
  { tag: '@demande-compte-conseiller' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('approves a national advisor ', async ({ page }) => {
      await page.goto('/projects/moderation');
      await page.locator('[data-test-id="advisor-view"]').click({ force: true });

      await page
        .locator("[data-test-id='moderation-advisor-card']", {
          hasText: 'nationalAdvisorRequest@test.fr',
        })
        .locator('[data-test-id="accept-advisor-access"]')
        .click();

      await page.goto('/projects/moderation');
      await expect(
        page.locator('[data-test-id="advisor-account-moderation-page"]')
      ).not.toContainText('nationalAdvisorRequest@test.fr');
    });

    test('refuses an advisor', async ({ page }) => {
      await page.goto('/projects/moderation');
      await page.locator('[data-test-id="advisor-view"]').click({ force: true });

      await page
        .locator("[data-test-id='moderation-advisor-card']", {
          hasText: 'refuseAdvisorRequest@test.fr',
        })
        .locator('[data-test-id="refuse-advisor-access"]')
        .click();

      await page.goto('/projects/moderation');
      await expect(
        page.locator('[data-test-id="advisor-account-moderation-page"]')
      ).not.toContainText('refuseAdvisorRequest@test.fr');
    });

    test('modify then accept a regional advisor', async ({ page }) => {
      await page.goto('/projects/moderation');
      await page.locator('[data-test-id="advisor-view"]').click({ force: true });

      await page
        .locator("[data-test-id='moderation-advisor-card']", {
          hasText: 'regionalAdvisorRequest@test.fr',
        })
        .locator('[data-test-id="modify-advisor-access"]')
        .click();

      await page.locator('[data-test-id="remove-selected-item"]').first().click();

      await page.locator('[data-test-id="save-modif-departments"]').click();

      await expect(
        page.locator(
          '[data-test-id="moderation-advisor-card"] [data-test-id="department-ask-for-access-advisor"]'
        )
      ).toHaveCount(1);

      await page
        .locator("[data-test-id='moderation-advisor-card']", {
          hasText: 'regionalAdvisorRequest@test.fr',
        })
        .locator('[data-test-id="accept-advisor-access"]')
        .click();

      // Check that the advisor is now in the list of advisors (NOT WORKING ON PROD)
      // cy.visit('/crm/users/?username=regionalAdvisor&role=1&ordering=');
      // cy.contains('NationalAdvisor');

      await page.goto('/projects/moderation');
      await expect(
        page.locator('[data-test-id="advisor-account-moderation-page"]')
      ).not.toContainText('regionalAdvisorRequest@test.fr');
    });
  }
);
