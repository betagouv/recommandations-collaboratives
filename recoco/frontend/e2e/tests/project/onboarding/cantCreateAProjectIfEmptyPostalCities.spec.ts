import project from '../../../../cypress/fixtures/projects/project.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I cant create a folder if the postal cities are empty',
  { tag: '@deposer-projet' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to the onboarding page and trigger an error if the postal is set but returns 0 cities', async ({
      page,
    }) => {
      await page.goto('/');

      await page
        .locator('[data-test-id="button-need-help"]', { hasText: 'Solliciter' })
        .click({ force: true });

      await expect(page).toHaveURL(/\/onboarding\/project/);

      const name = page.locator('#id_name');
      await expect(name).not.toHaveClass(/fr-input--error/);
      await name.fill(project.name);
      await expect(name).toHaveValue(project.name);
      await expect(name).toHaveClass(/fr-input--valid/);

      const location = page.locator('#id_location');
      await expect(location).not.toHaveClass(/fr-input--error/);
      await location.fill(project.location);
      await expect(location).toHaveValue(project.location);
      await expect(location).toHaveClass(/fr-input--valid/);

      const description = page.locator('#id_description');
      await expect(description).not.toHaveClass(/fr-input--error/);
      await description.fill(project.description);
      await expect(description).toHaveValue(project.description);
      await expect(description).toHaveClass(/fr-input--valid/);

      await page.locator('button[type="submit"]').click();

      await expect(page).toHaveURL(/\/onboarding\/project/);

      await expect(
        page.locator('[data-test-id="input-postcode"]').locator('..')
      ).toHaveClass(/fr-input-group--error/);

      await expect(
        page.locator('[data-test-id="select-city"]').locator('..')
      ).toHaveClass(/fr-select-group--error/);
    });
  }
);
