import { test as base, BrowserContext, Page } from '@playwright/test';

import { authFile } from '../helpers/users';

type AuthFixtures = {
  /**
   * Ouvre une nouvelle page connectée avec ce rôle (remplace les enchaînements
   * cy.logout() + cy.login(autreRôle) en cours de test). Les contextes ouverts
   * sont fermés automatiquement en fin de test.
   */
  loginAs: (role: string) => Promise<Page>;
};

export const test = base.extend<AuthFixtures>({
  loginAs: async ({ browser }, use) => {
    const contexts: BrowserContext[] = [];
    await use(async (role: string) => {
      const context = await browser.newContext({
        storageState: authFile(role),
      });
      contexts.push(context);
      return context.newPage();
    });
    for (const context of contexts) {
      await context.close();
    }
  },
});

export { expect } from '@playwright/test';
