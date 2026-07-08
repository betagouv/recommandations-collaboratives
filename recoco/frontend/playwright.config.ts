import dns from 'node:dns';
import { defineConfig, devices } from '@playwright/test';

import { ANONYMOUS_STATE } from './e2e/helpers/users';

// Node résout example.localhost en ::1 alors que le testserver Django écoute en IPv4.
// Chromium résout .localhost nativement ; ceci ne concerne que les requêtes API Node
// (setup d'auth, page.request).
dns.setDefaultResultOrder('ipv4first');

// Fichiers qui mutent un même état seedé et ne doivent pas se chevaucher :
// - projet 18 (« Mise en pause - Collectivité ») : pause/réactivation,
//   rejoindre/quitter ;
// - ressource 1 : édition du titre, des contacts et des départements.
// Exécutés sur un seul worker pour éviter qu'ils ne se marchent dessus.
const SHARED_STATE_MUTATORS = [
  /collectivity\/canPauseAProjectAsOwner\.spec\.ts/,
  /collectivity\/canQuitProjectAsProjectMember\.spec\.ts/,
  /collectivity\/cantQuitProjectAsProjectOwner\.spec\.ts/,
  /staff\/administration\/canQuitOrJoinProjectAsAdvisorOrObserver\.spec\.ts/,
  /staff\/administration\/canQuitProjectAsStaff\.spec\.ts/,
  /switchtender\/other\/canQuitOrJoinProjectAsAdvisorOrObserver\.spec\.ts/,
  /switchtender\/other\/canSeeProjectActiveStatus\.spec\.ts/,
  /resource\/canEditResource\.spec\.ts/,
  /searchableList\/canUpdateContactOfAResource\.spec\.ts/,
  /searchableList\/canUpdateDeparmentsOfAResource\.spec\.ts/,
];

export default defineConfig({
  testDir: './e2e',
  outputDir: './e2e/test-results',
  // Parallélisme au niveau fichier uniquement, comme cypress-parallel :
  // les tests d'un même fichier partagent souvent un état (projet créé en before).
  fullyParallel: false,
  workers: Number(process.env.PW_WORKERS ?? 2),
  retries: 2,
  timeout: 30_000,
  expect: { timeout: 10_000 },
  reporter: [
    ['html', { outputFolder: 'e2e/playwright-report', open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://example.localhost:8001',
    trace: 'on-first-retry',
    // État par défaut : non connecté, mais avec le cookie de consentement posé
    // (remplace le beforeEach global de cypress/support/e2e.js).
    storageState: ANONYMOUS_STATE,
  },
  projects: [
    {
      name: 'setup',
      testMatch: /setup\/.*\.setup\.ts/,
      // Les fichiers .auth n'existent pas encore au moment du setup.
      use: { storageState: { cookies: [], origins: [] } },
    },
    {
      name: 'chromium',
      testMatch: /tests\/.*\.spec\.ts/,
      testIgnore: SHARED_STATE_MUTATORS,
      dependencies: ['setup'],
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: 'chromium-serial',
      testMatch: SHARED_STATE_MUTATORS,
      dependencies: ['setup'],
      workers: 1,
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],
});
