import { expect, test } from '../../../fixtures';
import { checkCaptcha } from '../../../helpers/commands';

test.describe(
  'I can create a new project as a new user',
  { tag: '@deposer-projet' },
  () => {
    const projectInfo = {
      name: 'Test Project',
      location: '123 Test Street',
      postcode: 42424,
      insee: 42123,
      commune: 'commune de test',
      description: 'This is a test project description',
      email: `${Date.now()}@example.com`,
      fixedEmail: 'test2@example.com',
    };

    const signupInfo = {
      first_name: 'Test',
      last_name: 'User',
      organization: 'Test Organization',
      organization_position: 'Test Position',
      phone_no: '0102030405',
      password1: 'Testpassword123',
      password2: 'Testpassword123',
    };

    const alreadyExistingUserInfo = {
      email: projectInfo.email,
      password: 'Testpassword123',
    };

    test('goes through the complete onboarding process', async ({ page }) => {
      // Visit home page and click on need help button
      await page.goto('/');
      await page
        .locator('[data-test-id="button-need-help"]', { hasText: 'Solliciter' })
        .click({ force: true });

      // Land on onboarding/project page
      await expect(page).toHaveURL(/\/onboarding\/project/);

      // Fill project form
      const name = page.locator('#id_name');
      await expect(name).not.toHaveClass(/fr-input--error/);
      await name.fill(projectInfo.name);
      await expect(name).toHaveValue(projectInfo.name);
      await expect(name).toHaveClass(/fr-input--valid/);

      const location = page.locator('#id_location');
      await expect(location).not.toHaveClass(/fr-input--error/);
      await location.fill(projectInfo.location);
      await expect(location).toHaveValue(projectInfo.location);
      await expect(location).toHaveClass(/fr-input--valid/);

      const postcode = page.locator('[data-test-id="input-postcode"]');
      await postcode.pressSequentially(String(projectInfo.postcode));
      await expect(postcode).toHaveValue(String(projectInfo.postcode));
      await expect(postcode.locator('..')).toHaveClass(
        /fr-input-group--valid/
      );

      const city = page.locator('[data-test-id="select-city"]');
      await expect(city).not.toHaveClass(/fr-select-group--error/);
      await city.focus();

      await expect(city).toContainText(projectInfo.commune);
      await expect(city).toHaveValue(String(projectInfo.insee));
      await expect(city.locator('..')).toHaveClass(/fr-select-group--valid/);

      const description = page.locator('#id_description');
      await expect(description).not.toHaveClass(/fr-input--error/);
      await description.fill(projectInfo.description);
      await expect(description).toHaveValue(projectInfo.description);
      await expect(description).toHaveClass(/fr-input--valid/);

      const email = page.locator('#id_email');
      await expect(email).not.toHaveClass(/fr-input--error/);
      await email.fill(projectInfo.email);
      await expect(email).toHaveValue(projectInfo.email);
      await expect(email).toHaveClass(/fr-input--valid/);

      // Handle captcha
      await checkCaptcha(page);

      // Submit project form
      await page.locator('button[type="submit"]').click();

      // Land on onboarding/signup page
      await expect(page).toHaveURL(/\/onboarding\/signup/);

      // Fill signup form
      const firstName = page.locator('[name=first_name]');
      await firstName.fill(signupInfo.first_name);
      await expect(firstName).toHaveValue(signupInfo.first_name);

      const lastName = page.locator('[name=last_name]');
      await lastName.fill(signupInfo.last_name);
      await expect(lastName).toHaveValue(signupInfo.last_name);

      const orgName = page.locator('[name=org_name]');
      await orgName.fill(signupInfo.organization);
      await expect(orgName).toHaveValue(signupInfo.organization);

      const role = page.locator('[name=role]');
      await role.fill(signupInfo.organization_position);
      await expect(role).toHaveValue(signupInfo.organization_position);

      const phone = page.locator('[name=phone]');
      await phone.fill(signupInfo.phone_no);
      await expect(phone).toHaveValue(signupInfo.phone_no);

      await page.locator('[name=password]').fill('nope');

      await expect(page.locator('[id="error_0_password"]')).toBeVisible(); // min length error
      await expect(page.locator('[id="error_1_password"]')).toBeVisible(); // number error
      await expect(page.locator('[id="error_2_password"]')).toBeVisible(); // uppercase error

      await page.locator('[name=password]').clear();

      const password = page.locator('[name=password]');
      await password.fill(signupInfo.password1);
      await expect(password).toHaveValue(signupInfo.password1);

      await expect(page.locator('[id="valid_0_password"]')).toBeVisible(); // min length error
      await expect(page.locator('[id="valid_1_password"]')).toBeVisible(); // number error
      await expect(page.locator('[id="valid_2_password"]')).toBeVisible(); // uppercase error

      // Submit signup form
      await page.locator('[type=submit]').click();

      // Land on onboarding/summary page
      await expect(page).toHaveURL(/\/onboarding\/summary/);
    });

    test('goes through the onboarding process but stop at signup page', async ({
      page,
    }) => {
      // Visit home page and click on need help button
      await page.goto('/');
      await page
        .locator('[data-test-id="button-need-help"]', { hasText: 'Solliciter' })
        .click({ force: true });

      // Land on onboarding/project page
      await expect(page).toHaveURL(/\/onboarding\/project/);

      // Fill project form
      const name = page.locator('#id_name');
      await expect(name).not.toHaveClass(/fr-input--error/);
      await name.fill(projectInfo.name);
      await expect(name).toHaveValue(projectInfo.name);
      await expect(name).toHaveClass(/fr-input--valid/);

      const location = page.locator('#id_location');
      await expect(location).not.toHaveClass(/fr-input--error/);
      await location.fill(projectInfo.location);
      await expect(location).toHaveValue(projectInfo.location);
      await expect(location).toHaveClass(/fr-input--valid/);

      const postcode = page.locator('[data-test-id="input-postcode"]');
      await postcode.pressSequentially(String(projectInfo.postcode));
      await expect(postcode).toHaveValue(String(projectInfo.postcode));
      await expect(postcode.locator('..')).toHaveClass(
        /fr-input-group--valid/
      );

      const city = page.locator('[data-test-id="select-city"]');
      await expect(city).not.toHaveClass(/fr-select-group--error/);
      await city.focus();

      await expect(city).toContainText(projectInfo.commune);
      await expect(city).toHaveValue(String(projectInfo.insee));
      await expect(city.locator('..')).toHaveClass(/fr-select-group--valid/);

      const description = page.locator('#id_description');
      await expect(description).not.toHaveClass(/fr-input--error/);
      await description.fill(projectInfo.description);
      await expect(description).toHaveValue(projectInfo.description);
      await expect(description).toHaveClass(/fr-input--valid/);

      const email = page.locator('#id_email');
      await expect(email).not.toHaveClass(/fr-input--error/);
      await email.fill(projectInfo.fixedEmail);
      await expect(email).toHaveValue(projectInfo.fixedEmail);
      await expect(email).toHaveClass(/fr-input--valid/);

      // Handle captcha
      await checkCaptcha(page);

      // Submit project form
      await page.locator('button[type="submit"]').click();

      // Land on onboarding/signup page
      await expect(page).toHaveURL(/\/onboarding\/signup/);

      // Restart at project page
      await page.goto('/onboarding/project');

      await expect(
        page.locator('[data-cy="found-email-onboarding"]')
      ).toContainText(projectInfo.fixedEmail);

      await page.locator('[data-cy="continue-onboarding"]').click();

      // Fill signup form
      const firstName = page.locator('[name=first_name]');
      await firstName.fill(signupInfo.first_name);
      await expect(firstName).toHaveValue(signupInfo.first_name);

      const lastName = page.locator('[name=last_name]');
      await lastName.fill(signupInfo.last_name);
      await expect(lastName).toHaveValue(signupInfo.last_name);

      const orgName = page.locator('[name=org_name]');
      await orgName.fill(signupInfo.organization);
      await expect(orgName).toHaveValue(signupInfo.organization);

      const role = page.locator('[name=role]');
      await role.fill(signupInfo.organization_position);
      await expect(role).toHaveValue(signupInfo.organization_position);

      const phone = page.locator('[name=phone]');
      await phone.fill(signupInfo.phone_no);
      await expect(phone).toHaveValue(signupInfo.phone_no);

      const password = page.locator('[name=password]');
      await password.fill(signupInfo.password1);
      await expect(password).toHaveValue(signupInfo.password1);

      // Submit signup form
      await page.locator('[type=submit]').click();

      // Land on onboarding/summary page
      await expect(page).toHaveURL(/\/onboarding\/summary/);
    });

    test('goes through the complete onboarding process with already existing user', async ({
      page,
    }) => {
      // Visit home page and click on need help button
      await page.goto('/');
      await page
        .locator('[data-test-id="button-need-help"]', { hasText: 'Solliciter' })
        .click({ force: true });

      // Land on onboarding/project page
      await expect(page).toHaveURL(/\/onboarding\/project/);

      // Fill project form
      const name = page.locator('#id_name');
      await expect(name).not.toHaveClass(/fr-input--error/);
      await name.fill(projectInfo.name);
      await expect(name).toHaveValue(projectInfo.name);
      await expect(name).toHaveClass(/fr-input--valid/);

      const location = page.locator('#id_location');
      await expect(location).not.toHaveClass(/fr-input--error/);
      await location.fill(projectInfo.location);
      await expect(location).toHaveValue(projectInfo.location);
      await expect(location).toHaveClass(/fr-input--valid/);

      const postcode = page.locator('[data-test-id="input-postcode"]');
      await postcode.pressSequentially(String(projectInfo.postcode));
      await expect(postcode).toHaveValue(String(projectInfo.postcode));
      await expect(postcode.locator('..')).toHaveClass(
        /fr-input-group--valid/
      );

      const city = page.locator('[data-test-id="select-city"]');
      await expect(city).not.toHaveClass(/fr-select-group--error/);
      await city.focus();

      await expect(city).toContainText(projectInfo.commune);
      await expect(city).toHaveValue(String(projectInfo.insee));
      await expect(city.locator('..')).toHaveClass(/fr-select-group--valid/);

      const description = page.locator('#id_description');
      await expect(description).not.toHaveClass(/fr-input--error/);
      await description.fill(projectInfo.description);
      await expect(description).toHaveValue(projectInfo.description);
      await expect(description).toHaveClass(/fr-input--valid/);

      const email = page.locator('#id_email');
      await expect(email).not.toHaveClass(/fr-input--error/);
      await email.fill(projectInfo.email);
      await expect(email).toHaveValue(projectInfo.email);
      await expect(email).toHaveClass(/fr-input--valid/);

      // Handle captcha
      await checkCaptcha(page);

      // Submit project form
      await page.locator('button[type="submit"]').click();

      // Land on onboarding/signup page
      await expect(page).toHaveURL(/\/onboarding\/signin/);

      // Fill signup form
      await expect(page.locator('[name=login]')).toHaveValue(
        alreadyExistingUserInfo.email
      );

      const password = page.locator('[name=password]');
      await password.fill(alreadyExistingUserInfo.password);
      await expect(password).toHaveValue(alreadyExistingUserInfo.password);

      // Submit signup form
      await page.locator('[type=submit]').click();

      // Land on onboarding/summary page
      await expect(page).toHaveURL(/\/onboarding\/summary/);
    });
  }
);
