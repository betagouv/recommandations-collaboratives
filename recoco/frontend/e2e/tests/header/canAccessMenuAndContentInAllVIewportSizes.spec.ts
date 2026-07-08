import testDevices from '../../../cypress/fixtures/utils/devices.json';
import { expect, test } from '../../fixtures';
import { acceptCookies } from '../../helpers/commands';
import { ANONYMOUS_STATE } from '../../helpers/users';

test.describe.configure({ mode: 'serial' });

test.describe.skip(
  'As a visitor, I can access the menu and content on different devices',
  { tag: '@acces-rapide-utilisateur' },
  () => {
    const testLayouts = ['phone', 'tablet', 'desktop'];
    const breakpoint = 690;

    test.beforeAll(async ({ browser }) => {
      const context = await browser.newContext({
        storageState: ANONYMOUS_STATE,
      });
      const page = await context.newPage();
      await page.goto('/');
      await acceptCookies(page);
      await context.close();
    });

    for (const testItem of testLayouts) {
      test(`displays correctly on a ${testItem}`, async ({ page }) => {
        const devices = testDevices.devices.filter(
          ({ layout }) => layout === testItem
        );
        const layouts = testDevices.layouts.find(
          ({ name }) => name === testItem
        )!;

        for (const { dimensions } of devices) {
          const [width, height] = dimensions;
          let menuIsHidden = breakpoint > width;

          for (const orientation of layouts.config) {
            await page.goto('/');
            if (orientation === 'portrait') {
              await page.setViewportSize({ width, height });
            }
            if (orientation === 'landscape') {
              await page.setViewportSize({ width: height, height: width });
              menuIsHidden = breakpoint > height;
            }
            // Test here
            if (menuIsHidden) {
              await expect(
                page.locator('[data-test-id="secondary-menu"]')
              ).toBeHidden();
              // FIXME : this selector is no longer valid
              const toggler = page.locator(
                '[data-test-id="toggler-secondary-menu"]'
              );
              await expect(toggler).toBeVisible();
              await toggler.click();
              await expect(
                page
                  .locator('[data-test-id="secondary-menu"]')
                  .locator('[data-test-id="link-ressources"]')
              ).toBeVisible();
              // FIXME : this selector is no longer valid
              await toggler.click();
            } else {
              await expect(
                page.locator('[data-test-id="secondary-menu"]')
              ).toBeVisible();
              await expect(
                page
                  .locator('[data-test-id="secondary-menu"]')
                  .locator('[data-test-id="link-ressources"]')
              ).toBeVisible();
            }
          }
        }
      });
    }
  }
);
