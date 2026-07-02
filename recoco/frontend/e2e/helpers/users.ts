import path from 'node:path';

import users from '../../cypress/fixtures/users/users.json';

export const PASSWORD = 'Recoco2000';

// Mapping rôle → index dans users.json, extrait de cypress/support/commands.js (cy.login)
export const ROLE_TO_USER_INDEX: Record<string, number> = {
  staff: 0,
  jean: 1, // conseiller
  conseiller1: 1,
  jeanne: 2, // conseiller
  conseiller2: 2,
  jeannot: 3, // conseiller
  conseiller3: 3,
  bob: 4, // collectivité
  collectivité1: 4,
  boba: 5, // collectivité
  collectivité2: 5,
  bobette: 6, // collectivité
  collectivité3: 6,
  national: 7, // conseiller national
  nonactive: 8, // non active user
  regional: 11, // conseiller
  conseiller4: 11,
  regional2: 12, // conseiller
  conseiller5: 12,
  staffOnSite: 13,
};

// Rôles pour lesquels une session est établie au setup ('nonactive' ne peut pas
// ouvrir de session, les alias jean/bob/... pointent vers les mêmes utilisateurs).
export const CANONICAL_ROLES = [
  'staff',
  'staffOnSite',
  'conseiller1',
  'conseiller2',
  'conseiller3',
  'conseiller4',
  'conseiller5',
  'collectivité1',
  'collectivité2',
  'collectivité3',
  'national',
];

export function usernameFor(role: string): string {
  const index = ROLE_TO_USER_INDEX[role];
  if (index === undefined) {
    throw new Error(`Rôle inconnu : ${role}`);
  }
  return users[index].fields.username;
}

export const AUTH_DIR = path.resolve(__dirname, '../.auth');
export const ANONYMOUS_STATE = path.join(AUTH_DIR, 'anonymous.json');

/** Chemin du storageState du rôle ; un fichier par utilisateur canonique. */
export function authFile(role: string): string {
  const index = ROLE_TO_USER_INDEX[role];
  if (index === undefined) {
    throw new Error(`Rôle inconnu : ${role}`);
  }
  return path.join(AUTH_DIR, `user-${index}.json`);
}

// Cookie posé pour neutraliser le bandeau de consentement (composant Consent.js :
// le banner est masqué dès qu'un cookie dont le nom contient "cookie_consent" est
// présent). Sans lui, le bandeau couvre les inputs — cf. cypress/support/e2e.js.
export const CONSENT_COOKIE = {
  name: 'cookie_consent',
  value: 'preferences=2999-01-01T00:00:00',
  domain: 'example.localhost',
  path: '/',
  expires: -1,
  httpOnly: false,
  secure: false,
  sameSite: 'Lax' as const,
};
