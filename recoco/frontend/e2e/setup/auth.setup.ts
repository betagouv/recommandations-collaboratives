import fs from 'node:fs';

import { expect, request, test as setup } from '@playwright/test';

import {
  ANONYMOUS_STATE,
  AUTH_DIR,
  CANONICAL_ROLES,
  CONSENT_COOKIE,
  PASSWORD,
  authFile,
  usernameFor,
} from '../helpers/users';

// storageState par défaut des tests : non connecté, cookie de consentement posé.
setup('anonymous state', async () => {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(
    ANONYMOUS_STATE,
    JSON.stringify({ cookies: [CONSENT_COOKIE], origins: [] }, null, 2)
  );
});

// Login programmatique par rôle (réplique du flux CSRF de cy.login, sans navigateur) :
// GET /accounts/login/ pose le csrftoken, puis POST du formulaire de connexion.
for (const role of CANONICAL_ROLES) {
  setup(`authenticate ${role}`, async ({ baseURL }) => {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
    const context = await request.newContext({ baseURL });
    await context.get('/accounts/login/');
    const csrf = (await context.storageState()).cookies.find(
      (cookie) => cookie.name === 'csrftoken'
    );
    expect(csrf, 'csrftoken attendu après GET /accounts/login/').toBeTruthy();

    const response = await context.post('/accounts/login/', {
      form: {
        login: usernameFor(role),
        password: PASSWORD,
        csrfmiddlewaretoken: csrf!.value,
      },
      headers: { Referer: `${baseURL}/accounts/login/` },
    });
    expect(response.ok()).toBeTruthy();

    const state = await context.storageState();
    expect(state.cookies.map((cookie) => cookie.name)).toContain('sessionid');
    state.cookies.push(CONSENT_COOKIE);
    fs.writeFileSync(authFile(role), JSON.stringify(state, null, 2));
    await context.dispose();
  });
}
