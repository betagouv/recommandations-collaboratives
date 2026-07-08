import { expect, test } from '../../../fixtures';

test.describe(
  'I can follow the onboarding advisor tutorial as an advisor or staff',
  { tag: '@tutoriel-onboarding-conseiller' },
  () => {
    test('should not display the tutorial when a collectivity is on a project presentation page', async ({
      loginAs,
    }) => {
      const page = await loginAs('collectivité1');
      await page.goto('/project/2');
      await expect(
        page.locator('[data-test-id="opening-onboarding-tutorial"]')
      ).toHaveCount(0);
    });

    test('follows the tutorial steps correctly if not already advising the project', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller2');
      await page.goto('/project/2');

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-1"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="select-observer-or-advisor-button"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="button-become-advisor"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-1"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-2"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="project-navigation-knowledge"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-2"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-3"]')
        .dispatchEvent('click');
      // La navigation vers l'onglet conversations peut ne pas aboutir sous
      // charge : on re-clique jusqu'à ce que l'éditeur apparaisse.
      await expect(async () => {
        await page
          .locator('[data-test-id="project-navigation-conversations-new"]')
          .dispatchEvent('click');
        await expect(
          page.locator('[data-test-id="tiptap-editor-content"]')
        ).toBeAttached({ timeout: 3_000 });
      }).toPass({ timeout: 15_000 });
      await page
        .locator('[data-test-id="tiptap-editor-content"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-3"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-4"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="button-invite-collaborators"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="link-invite-collaborators"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="button-invite-collaborators"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-4"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="project-navigation-overview"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="opening-onboarding-tutorial"]')
      ).toHaveCount(0);
    });

    test('follows the tutorial steps correctly if already advising the project', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller1');
      await page.goto('/project/2');

      await expect(
        page
          .locator('[data-test-id="onboarding-tutorial__popup-content"]')
          .first()
      ).toBeAttached();
      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-1"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-1"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-2"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="project-navigation-knowledge"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-2"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-3"]')
        .dispatchEvent('click');
      // La navigation vers l'onglet conversations peut ne pas aboutir sous
      // charge : on re-clique jusqu'à ce que l'éditeur apparaisse.
      await expect(async () => {
        await page
          .locator('[data-test-id="project-navigation-conversations-new"]')
          .dispatchEvent('click');
        await expect(
          page.locator('[data-test-id="tiptap-editor-content"]')
        ).toBeAttached({ timeout: 3_000 });
      }).toPass({ timeout: 15_000 });
      await page
        .locator('[data-test-id="tiptap-editor-content"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-3"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="onboarding-tutorial__popup-challenge-4"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="button-invite-collaborators"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="link-invite-collaborators"]')
        .dispatchEvent('click');
      await page
        .locator('[data-test-id="button-invite-collaborators"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="onboarding-tutorial__popup-challenge-4"]')
      ).toHaveCount(0);

      await page
        .locator('[data-test-id="project-navigation-overview"]')
        .dispatchEvent('click');
      await expect(
        page.locator('[data-test-id="opening-onboarding-tutorial"]')
      ).toHaveCount(0);
    });
  }
);
