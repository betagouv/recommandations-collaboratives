import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

const urls = [
  '/',
  '/accessibilite',
  // '/accounts/2fa/',
  // '/accounts/2fa/authenticate/',
  // '/accounts/2fa/reauthenticate/',
  // '/accounts/email/',
  // '/accounts/inactive/',
  // '/accounts/login/',
  // '/accounts/logout/',
  // '/accounts/password/change/',
  // '/accounts/password/reset/',
  // '/accounts/password/reset/done/',
  // '/accounts/password/set/',
  // '/accounts/signup/',
  // '/accounts/social/connections/',
  // '/accounts/social/login/cancelled/',
  // '/accounts/social/login/error/',
  '/acteurs-locaux',
  '/addressbook/contacts/',
  '/addressbook/organizations/',
  '/addressbook/organizations/create',
  '/cms/',
  '/conditions-generales-utilisation',
  '/confidentialite',
  '/contact/',
  '/cookies/',
  '/crm/',
  // '/crm/feed/', // XML
  '/crm/low-reach-projects',
  // '/crm/low-reach-projects-csv', // CSV
  '/crm/org/',
  // '/crm/org/merge/',
  '/crm/project/',
  '/crm/project/activity',
  '/crm/projects/by_tags',
  // '/crm/projects/by_tags.csv', // CSV
  '/crm/reco_without_resources',
  '/crm/search',
  '/crm/site_config',
  '/crm/site_config/tags',
  '/crm/tags',
  '/crm/topics',
  // '/crm/topics/csv', // CSV
  '/crm/users/',
  // '/documents/', // Not found
  // '/dsrc-form/', // Not found
  // '/dsrc/', // Not found
  // '/hit/', // Api
  // '/login-redirect', // Redirect
  // '/logout/',
  // '/markdownx/', // Not found
  '/mentions-legales',
  '/methodologie',
  '/nimda/',
  '/nous-suivre',
  // '/onboarding', // Redirect
  // '/onboarding/prefill/project', // Redirect
  '/onboarding/prefill/setuser',
  '/onboarding/project',
  // '/onboarding/signin', // Redirect
  // '/onboarding/signup', // Redirect
  '/projects/',
  '/projects/action/',
  // '/projects/advisor/', // Redirect
  // '/projects/csv', // CSV
  // '/projects/feed/', // XML
  '/projects/map',
  '/projects/moderation/',
  // '/projects/staff/', // Redirect
  '/projects/task-recommendation',
  '/projects/task-recommendation/create',
  '/qui-sommes-nous',
  '/ressource/',
  '/ressource/create/',
  // '/ressource/feed/', // XML
  '/schema-multi-annuel',
  '/securite',
  // '/setup-password/', // Redirect
  '/site/create',
  '/stats',
  // '/survey/editor/survey/', // Not found
];

// URLs avec paramètres dynamiques (remplacer les {param} par des valeurs réelles)
const dynamicUrls = [
  '/addressbook/contact/1/update/',
  // '/addressbook/organization/2/',
  '/addressbook/organization/2/create',
  // '/addressbook/organization/2/update/',
  // '/advisor-access-request', // Redirect
  // '/advisor-access-request/{advisor_access_request_id}/', // Redirect
  '/crm/org/2/',
  '/crm/org/2/create-note',
  '/crm/org/2/update/',
  '/crm/project/1/',
  '/crm/project/1/create-note',
  '/crm/project/1/delete/',
  '/crm/project/1/handover',
  '/crm/project/1/update/',
  '/crm/user/2/',
  '/crm/user/2/create-note',
  '/crm/user/2/notifications',
  '/crm/user/2/reminders',
  '/crm/user/2/update/',
  '/onboarding/summary/1',
  // '/project/partage/{project_ro_key}/',
  // '/project/survey/{session_id}/results',
  '/project/1/presentation',
  '/project/1/activite',
  '/project/1/administration/',
  '/project/1/connaissance',
  '/project/1/conversations',
  '/project/1/documents',
  '/project/1/location',
  '/project/1/note/',
  '/project/1/suggestions/',
  '/project/1/suivi',
  // '/project/1/survey', // Redirect
  '/project/1/tags',
  '/project/1/topics',
  '/ressource/1/revision/',
  '/ressource/1/',
  '/ressource/1/embed',
  '/ressource/1/update/',
];

test.use({ storageState: authFile('staff') });

test.describe('I can explore all urls', { tag: '@can-explore-all-urls' }, () => {
  for (const url of urls) {
    test(`explore static url : ${url}`, async ({ page }) => {
      const response = await page.goto(url);
      expect(response?.status()).toBe(200);
    });
  }
  for (const url of dynamicUrls) {
    test(`explore dynamic url : ${url}`, async ({ page }) => {
      const response = await page.goto(url);
      expect(response?.status()).toBe(200);
    });
  }
});
