import { expect, test } from '../../fixtures';
import { checkCaptcha } from '../../helpers/commands';

test.describe(
  'As a visitor to a recoco site, I can find a way to contact the site team',
  { tag: '@contact-equipe' },
  () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
    });

    test('Displays a contact form or a contact email', async ({ page }) => {
      await page.goto('/contact');

      await page
        .locator('[data-test-id="contact-form-name"]')
        .fill('Cecile Ménard');
      await page
        .locator('[data-test-id="contact-form-email"]')
        .fill('cecile@example.com');
      await page
        .locator('[data-test-id="contact-form-subject"]')
        .fill('Premier contact');
      await page
        .locator('[data-test-id="contact-form-message"]')
        .fill(
          "Bonjour, Ma commune a une friche qu'on souhaite réhabiliter. Comment faire ?"
        );

      await checkCaptcha(page, 500);

      await page
        .locator('[data-test-id="contact-form-submit"]')
        .click({ force: true });

      await expect(
        page.getByText(`Merci, votre demande a été transmis à l'équipe`)
      ).toBeVisible();
    });
  }
);
