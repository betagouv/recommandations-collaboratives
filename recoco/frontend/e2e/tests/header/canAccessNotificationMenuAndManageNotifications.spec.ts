import { expect, test } from '../../fixtures';
import { typeInTiptapEditor } from '../../helpers/commands';
import { authFile } from '../../helpers/users';

test.describe.configure({ mode: 'serial' });

test.describe(
  'As a switchtender I can manage notifications in header',
  { tag: '@liste-notifications' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeAll(async ({ browser }) => {
      const context = await browser.newContext({
        storageState: authFile('collectivité1'),
      });
      const page = await context.newPage();
      await page.goto('/project/2/conversations');

      const sendButton = page.locator(
        '[data-test-id="send-message-conversation"]'
      );
      for (let i = 0; i < 4; i++) {
        // La frappe peut partir avant l'hydratation de TipTap : on retape
        // jusqu'à ce que le bouton d'envoi s'active.
        await expect(async () => {
          await typeInTiptapEditor(page, 'Here is my contact');
          await expect(sendButton).toBeEnabled({ timeout: 2_000 });
        }).toPass();
        await sendButton.click();
        // Le bouton se désactive une fois le message parti et l'éditeur vidé
        await expect(sendButton).toBeDisabled();
      }

      await context.close();
    });

    test('displays badge notification in the menu', async ({ page }) => {
      await page.goto('/');
      const badge = page.locator('[data-test-id="notification-badge"]');
      expect(Number(await badge.textContent())).toBeGreaterThan(0);
    });

    test('displays a button to open and close notification menu', async ({
      page,
    }) => {
      await page.goto('/');
      await page.locator('[data-test-id="notification-menu-open"]').click();
      const menu = page.locator('.dropdown-menu.notifications');
      await expect(menu).toBeVisible();
      await expect(menu).toHaveClass(/show/);
      await page.locator('[data-test-id="notification-menu-open"]').click();
      // Le menu fermé est masqué par clipping (overflow d'un ancêtre), que
      // Playwright considère toujours « visible » : on vérifie l'état Bootstrap.
      await expect(menu).not.toHaveClass(/show/);
    });

    test('displays a button to mark notification as read one by one', async ({
      page,
    }) => {
      await page.goto('/');
      const badge = page.locator('[data-test-id="notification-badge"]');
      const notificationNumber = Number(await badge.textContent());
      expect(notificationNumber).toBeGreaterThan(0);
      await page.locator('[data-test-id="notification-menu-open"]').click();

      // Élément du menu clippé par l'overflow : équivalent du force:true Cypress
      await page
        .locator('[data-test-id="notification-mark-as-read-one"]')
        .first()
        .dispatchEvent('click');
      await expect
        .poll(async () => Number(await badge.textContent()))
        .toBe(notificationNumber - 1);
    });

    test('displays a button to mark all notifications as read', async ({
      page,
    }) => {
      await page.goto('/');
      const badge = page.locator('[data-test-id="notification-badge"]');
      const notificationNumber = Number(await badge.textContent());
      expect(notificationNumber).toBeGreaterThan(0);
      await page.locator('[data-test-id="notification-menu-open"]').click();
      // Élément du menu clippé par l'overflow : équivalent du force:true Cypress
      await page
        .locator('[data-test-id="notification-mark-all-as-read"]')
        .dispatchEvent('click');
      await page.waitForTimeout(400);
      await expect(
        page.locator('[data-test-id="notification-mark-all-as-read"]')
      ).toBeDisabled();
      await expect(
        page.locator('[data-test-id="notification-badge"]')
      ).toBeHidden();
    });
  }
);
