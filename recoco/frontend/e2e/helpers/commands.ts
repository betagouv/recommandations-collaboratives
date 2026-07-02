/**
 * Port Playwright des commandes custom Cypress (cypress/support/commands.js).
 * Chaque commande devient une fonction libre prenant `page` en premier argument.
 */

import { Browser, Locator, Page, expect } from '@playwright/test';

import communes from '../../cypress/fixtures/geomatics/commune.json';
import project from '../../cypress/fixtures/projects/project.json';
import resources from '../../cypress/fixtures/resources/resources.json';
import { PASSWORD, authFile, usernameFor } from './users';

const currentResource = resources[4];
const currentResourceTitle = currentResource.fields.title as string;
const projectCommune = communes.find(
  (commune) => String(commune.fields.postal) === String(project.postcode)
)!;

export type ProjectFixture = typeof project;

/**
 * Login via le formulaire (le login par API + storageState est fait au setup ;
 * cette fonction ne sert que pour 'nonactive' et les tests de la page de login).
 */
export async function loginViaForm(page: Page, role: string) {
  await page.goto('/accounts/login/');
  await page.locator('#id_login').fill(usernameFor(role));
  await page.locator('#id_password').fill(PASSWORD);
  await page.locator('[type=submit]').click();
}

export async function logout(page: Page) {
  await page.goto('/accounts/logout/');
}

export async function acceptCookies(page: Page) {
  await page
    .locator('[data-test-id="fr-consent-banner"]')
    .locator('[data-test-id="button-consent-accept-all"]')
    .click({ force: true });
  await page.goto('/');
}

export async function declineCookies(page: Page) {
  await page
    .locator('[data-test-id="fr-consent-banner"]')
    .locator('[data-test-id="button-consent-decline-all"]')
    .click({ force: true });
  await page.goto('/');
}

export async function hideCookieBannerAndDjango(page: Page) {
  await page
    .locator('[data-test-id="fr-consent-banner"]')
    .locator('[data-test-id="button-consent-accept-all"]')
    .click();
  await page.locator('#djHideToolBarButton').click();
}

/**
 * Attend l'initialisation d'Alpine.js. Nécessaire avant de remplir un
 * formulaire piloté par x-model : un fill() antérieur à l'hydratation met la
 * valeur dans le DOM mais pas dans le store Alpine soumis par le formulaire.
 */
export async function waitForAlpine(page: Page) {
  await page.waitForFunction(
    () => (window as unknown as { Alpine?: unknown }).Alpine !== undefined
  );
}

/** Coche la case du faux reCAPTCHA (RECAPTCHA_REQUIRED_SCORE=0 en settings e2e). */
export async function checkCaptcha(page: Page, waitMs = 400) {
  await page
    .frameLocator('#id_captcha iframe[title="reCAPTCHA"]')
    .locator('.recaptcha-checkbox')
    .click();
  await page.waitForTimeout(waitMs);
}

/**
 * Crée un projet via le parcours d'onboarding complet et retourne son id
 * (remplace l'alias Cypress @projectId, qui n'était consommé nulle part).
 */
export async function createProject(
  page: Page,
  label?: string,
  objProject: ProjectFixture = project,
  isSignupRequired = false,
  userToSignup: Record<string, string> = {}
): Promise<string> {
  await page.goto('/');

  await page
    .locator('[data-test-id="button-need-help"]', { hasText: 'Solliciter' })
    .click({ force: true });

  await expect(page).toHaveURL(/\/onboarding\/project/);

  const name = label || objProject.name || project.name;
  const nameInput = page.locator('#id_name');
  await expect(nameInput).not.toHaveClass(/fr-input--error/);
  await nameInput.fill(name);
  await expect(nameInput).toHaveValue(name);
  await expect(nameInput).toHaveClass(/fr-input--valid/);

  if (isSignupRequired) {
    const email = userToSignup['[name=email]'];
    const emailInput = page.locator('#id_email');
    await expect(emailInput).not.toHaveClass(/fr-input--error/);
    await emailInput.fill(email);
    await expect(emailInput).toHaveValue(email);
    await expect(emailInput).toHaveClass(/fr-input--valid/);
  }

  const location = objProject.location || project.location;
  const locationInput = page.locator('#id_location');
  await expect(locationInput).not.toHaveClass(/fr-input--error/);
  await locationInput.fill(location);
  await expect(locationInput).toHaveValue(location);
  await expect(locationInput).toHaveClass(/fr-input--valid/);

  const postcode = String(objProject.postcode || project.postcode);
  const postcodeInput = page.locator('[data-test-id="input-postcode"]');
  await expect(postcodeInput.locator('..')).not.toHaveClass(
    /fr-input-group--error/
  );
  // L'autocomplétion commune (CitySelect) écoute les frappes : pas de fill().
  await postcodeInput.pressSequentially(postcode);
  await expect(postcodeInput).toHaveValue(postcode);
  await expect(postcodeInput.locator('..')).toHaveClass(
    /fr-input-group--valid/
  );

  const citySelect = page.locator('[data-test-id="select-city"]');
  await expect(citySelect.locator('..')).not.toHaveClass(
    /fr-select-group--error/
  );
  await citySelect.focus();
  await expect(citySelect).toContainText(projectCommune.fields.name);
  await expect(citySelect).toHaveValue(String(projectCommune.fields.insee));
  await expect(citySelect.locator('..')).toHaveClass(/fr-select-group--valid/);

  const description = objProject.description || project.description;
  const descriptionInput = page.locator('#id_description');
  await expect(descriptionInput).not.toHaveClass(/fr-input--error/);
  await descriptionInput.fill(description);
  await expect(descriptionInput).toHaveValue(description);
  await expect(descriptionInput).toHaveClass(/fr-input--valid/);

  await checkCaptcha(page);

  await page.locator('button[type="submit"]').click();

  if (isSignupRequired) {
    await expect(page).toHaveURL(/\/onboarding\/signup/);
    for (const [selector, value] of Object.entries(userToSignup)) {
      if (selector !== '[name=email]') {
        await page.locator(selector).fill(value);
      }
    }
    await page.locator('[type=submit]').click();
  }

  await expect(page).toHaveURL(/\/onboarding\/summary/);

  const idMatch = page.url().match(/\/onboarding\/summary\/(\d+)$/);
  if (!idMatch) {
    throw new Error("ID non trouvé dans l'URL");
  }
  return idMatch[1];
}

async function postWithCsrf(page: Page, url: string) {
  const csrf = (await page.context().cookies()).find(
    (cookie) => cookie.name === 'csrftoken'
  );
  if (!csrf) {
    throw new Error('Cookie csrftoken introuvable');
  }
  const response = await page.request.post(url, {
    headers: { 'X-CSRFToken': csrf.value, Referer: page.url() },
  });
  expect(response.ok()).toBeTruthy();
}

/** Rejoint le projet comme conseiller (appel API, comme cy.becomeAdvisor). */
export async function becomeAdvisor(page: Page, projectId: string | number) {
  await postWithCsrf(page, `/project/${projectId}/switchtender/join`);
}

/** Rejoint le projet comme observateur (appel API, comme cy.becomeObserver). */
export async function becomeObserver(page: Page, projectId: string | number) {
  await postWithCsrf(page, `/project/${projectId}/observer/join`);
}

/** Crée une recommandation depuis la page actions (port de cy.createTask). */
export async function createTask(
  page: Page,
  label: string,
  topic = '',
  withResource = false,
  draft = false
) {
  // Les boutons sont rendus par Alpine après hydratation : contrairement à
  // cy.get(...), page.count() ne réessaie pas, donc on attend qu'au moins l'un
  // des deux apparaisse avant de compter.
  await expect(
    page
      .locator(
        '[data-test-id="submit-task-button"], [data-test-id="create-task-button"]'
      )
      .first()
  ).toBeAttached();
  const hasSubmitButton =
    (await page.locator('[data-test-id="submit-task-button"]').count()) > 0;
  const hasCreateButton =
    (await page.locator('[data-test-id="create-task-button"]').count()) > 0;

  if (hasSubmitButton) {
    await page
      .getByText('Émettre une recommandation')
      .first()
      .click({ force: true });

    await page.locator('.ProseMirror p').first().click();
    await page.keyboard.type('text');

    if (!withResource) {
      await page.locator('#push-noresource').click({ force: true });
      const intent = page.locator('#intent');
      await intent.fill(label);
      await expect(intent).toHaveValue(label);
    } else {
      await page.locator('#push-single').click({ force: true });
      await page
        .locator('[data-test-id="search-resource-input"]')
        .pressSequentially(currentResourceTitle);
      await page
        .locator(`#resource-${currentResource.pk}`)
        .check({ force: true });
    }

    if (topic !== '') {
      const topicInput = page.locator('#topic_name');
      await topicInput.pressSequentially(topic);
      await expect(topicInput).toHaveValue(topic);
    }

    if (draft) {
      await page.locator('[data-test-id="publish-draft-task-button"]').click();
    } else {
      const submit = page.locator('[type=submit]');
      await expect(submit).toBeEnabled();
      await submit.click({ force: true });
    }

    await expect(page).toHaveURL(/\/conversations/);

    if (!withResource) {
      await expect(page.getByText(label).first()).toBeVisible();
    } else {
      await expect(
        page.getByText(currentResourceTitle).first()
      ).toBeVisible();
    }
  } else if (hasCreateButton) {
    // Le bouton est un toggle de menu dans le composer (conteneur display:none) ;
    // Cypress dispatchait le clic sur l'élément (force:true). Il ouvre un menu
    // dont « Recommandation vierge » navigue vers la page de création.
    await page
      .locator('[data-test-id="create-task-button"]')
      .first()
      .dispatchEvent('click');
    await page.getByText('Recommandation vierge').first().dispatchEvent('click');
    await page.waitForURL(/\/projects\/action/);

    await page.locator('#push-noresource').click({ force: true });
    const intent = page.locator('#intent');
    await intent.fill(label);
    await expect(intent).toHaveValue(label);

    await page.locator('.ProseMirror p').first().click();
    await page.keyboard.type('text');

    if (draft) {
      await page.locator('[data-test-id="publish-draft-task-button"]').click();
    } else {
      const submit = page.locator('[type=submit]');
      await expect(submit).toBeEnabled();
      await submit.click({ force: true });
    }

    await expect(page).toHaveURL(/\/conversations/);
  } else {
    throw new Error("can't create task");
  }
}

/**
 * Approuve un projet via l'admin Django, avec un contexte staff dédié
 * (remplace le cy.login('staff') destructeur de session de cy.approveProject).
 */
export async function approveProject(browser: Browser, index: number | string) {
  const context = await browser.newContext({
    storageState: authFile('staff'),
  });
  const page = await context.newPage();

  await page.goto('/nimda/projects/project/');
  await page
    .locator('tr', { hasText: `${project.name} ${index}` })
    .locator('th.field-created_on a')
    .click({ force: true });

  await page.locator('#id_status').selectOption({ index: 1 });
  const lastName = page.locator('#id_last_name');
  await lastName.fill(`${project.last_name} ${index}`);
  await expect(lastName).toHaveValue(`${project.last_name} ${index}`);
  const firstName = page.locator('#id_first_name');
  await firstName.fill(`${project.first_name} ${index}`);
  await expect(firstName).toHaveValue(`${project.first_name} ${index}`);
  await page.getByText('Enregistrer', { exact: true }).first().click();

  await context.close();
}

/** Ouvre un projet depuis le menu projets (port de cy.navigateToProject). */
export async function navigateToProject(page: Page, index: number | string) {
  await page.goto('/');
  await page.locator('#projects-list-button').click({ force: true });
  await page
    .getByText(`${project.name} ${index}`)
    .first()
    .click({ force: true });
}

/**
 * Vérifie qu'une image se charge et que son attribut alt correspond à son rôle
 * ARIA (port de la child command cy.testImage).
 */
export async function expectValidImage(
  image: Locator,
  role: 'img-informative' | 'img-presentation' | 'img-functional',
  type: 'svg' | 'png' | 'jpg' | 'jpeg'
) {
  const alt = await image.getAttribute('alt');
  expect(alt).not.toBeNull();
  await expect(image).not.toHaveJSProperty('src', '');

  switch (role) {
    case 'img-presentation':
      expect(alt).toBe('');
      break;
    case 'img-functional':
    case 'img-informative':
      expect(alt).not.toBe('');
      break;
  }

  switch (type) {
    case 'svg':
      await expect
        .poll(() =>
          image.evaluate((img) => (img as HTMLImageElement).width)
        )
        .toBeGreaterThan(0);
      expect(alt).toBe('');
      break;
    case 'png':
    case 'jpg':
    case 'jpeg':
      // naturalWidth n'est renseigné que quand l'image est chargée
      await expect
        .poll(() =>
          image.evaluate((img) => (img as HTMLImageElement).naturalWidth)
        )
        .toBeGreaterThan(0);
      break;
  }
}

/** Recherche et attache un contact dans l'éditeur (port de cy.shareContact). */
export async function shareContact(page: Page, name: string) {
  await page
    .locator('[data-test-id="button-add-contact-in-editor"]')
    .click({ force: true });
  await page.locator('#search-contact-input').pressSequentially(name);
  await page
    .locator('[data-test-id="contact-card"]')
    .first()
    .click({ force: true });
  await page
    .locator('[data-test-id="button-add-contact-to-tiptap-editor"]')
    .click({ force: true });
}

/** Saisit du texte dans l'éditeur TipTap (ProseMirror ignore fill()). */
export async function typeInTiptapEditor(page: Page, text: string) {
  const editor = page
    .locator('[data-test-id="tiptap-editor-content"] .ProseMirror')
    .first();
  // Focus programmatique : l'éditeur peut être hors écran ou masqué au moment
  // de la frappe (le .type({ force: true }) Cypress passait outre). La frappe
  // est revérifiée car TipTap peut ne pas encore être hydraté au premier essai.
  await editor.waitFor({ state: 'attached' });
  await expect(async () => {
    await editor.evaluate((el) => (el as HTMLElement).focus());
    await page.keyboard.type(text);
    const content = (await editor.textContent()) ?? '';
    expect(content).toContain(text);
  }).toPass({ timeout: 15_000 });
}
