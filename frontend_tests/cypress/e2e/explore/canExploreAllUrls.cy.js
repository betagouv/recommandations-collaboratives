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
  '/project/1/overview',
  '/project/1/actions',
  '/project/1/actions/inline',
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
describe('I can explore all urls @can-explore-all-urls', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  for (const url of urls) {
    it(`explore static url : ${url}`, function () {
      cy.intercept('GET', url).as(`${url}Page`);
      cy.visit(url);
      cy.wait(`@${url}Page`).its('response.statusCode').should('eq', 200);
    });
  }
  for (const url of dynamicUrls) {
    it(`explore dynamic url : ${url}`, function () {
      cy.intercept('GET', url).as(`${url}Page`);
      cy.visit(url);
      cy.wait(`@${url}Page`).its('response.statusCode').should('eq', 200);
    });
  }
});

/**
 *
 *
// URLs avec paramètres dynamiques (remplacer les {param} par des valeurs réelles)
const dynamicUrls = [
  '/addressbook/contact/1/update/',
  '/addressbook/organization/2/',
  '/addressbook/organization/2/create',
  '/addressbook/organization/2/update/',
  '/advisor-access-request',
  '/advisor-access-request/{advisor_access_request_id}/',
  '/crm/org/2/',
  '/crm/org/2/create-note',
  '/crm/org/2/note/{note_id}',
  '/crm/org/2/update/',
  '/crm/project/1/',
  '/crm/project/1/annotation/toggle/',
  '/crm/project/1/create-note',
  '/crm/project/1/delete/',
  '/crm/project/1/handover',
  '/crm/project/1/note/{note_id}',
  '/crm/project/1/undelete/',
  '/crm/project/1/update/',
  '/crm/user/2/',
  '/crm/user/2/advisor/set/',
  '/crm/user/2/advisor/unset/',
  '/crm/user/2/create-note',
  '/crm/user/2/deactivate/',
  '/crm/user/2/note/{note_id}',
  '/crm/user/2/notifications',
  '/crm/user/2/reactivate/',
  '/crm/user/2/reminders',
  '/crm/user/2/reminders/{reminder_pk}',
  '/crm/user/2/update/',
  '/invites/{invite_id}',
  '/invites/{invite_id}/accept',
  '/invites/{invite_id}/refuse',
  '/note/{note_id}/',
  '/note/{note_id}/delete/',
  '/oidc/{provider_id}/login/',
  '/oidc/{provider_id}/login/callback/',
  '/onboarding/summary/1',
  '/project/partage/{project_ro_key}/',
  '/project/survey/{session_id}/results',
  '/project/1/',
  '/project/1/actions',
  '/project/1/actions/inline',
  '/project/1/activite',
  '/project/1/administration/',
  '/project/1/administration/access/advisor/invite',
  '/project/1/administration/access/advisor/invite/{invite_id}/resend',
  '/project/1/administration/access/advisor/{username}/delete',
  '/project/1/administration/access/collectivity/invite',
  '/project/1/administration/access/collectivity/invite/{invite_id}/resend',
  '/project/1/administration/access/collectivity/{username}/delete',
  '/project/1/administration/access/invite/{invite_id}/revoke',
  '/project/1/administration/set-active',
  '/project/1/administration/set-inactive',
  '/project/1/administration/2/promote/',
  '/project/1/connaissance',
  '/project/1/conversations',
  '/project/1/delete/',
  '/project/1/documents',
  '/project/1/documents/televerser',
  '/project/1/documents/{document_id}/delete',
  '/project/1/documents/{document_id}/pin-unpin',
  '/project/1/location',
  '/project/1/note/',
  '/project/1/observer/join',
  '/project/1/presentation',
  '/project/1/recommandations/embed',
  '/project/1/suggestions/',
  '/project/1/suivi',
  '/project/1/survey',
  '/project/1/survey/{site_id}',
  '/project/1/switchtender/join',
  '/project/1/switchtender/leave',
  '/project/1/tags',
  '/project/1/topics',
  '/projects/moderation/advisor/{advisor_access_request_id}/accept/',
  '/projects/moderation/advisor/{advisor_access_request_id}/modify/',
  '/projects/moderation/advisor/{advisor_access_request_id}/refuse/',
  '/projects/moderation/project/1/accept/',
  '/projects/moderation/project/1/refuse/',
  '/projects/survey/{session_id}/',
  '/projects/survey/{session_id}/done',
  '/projects/survey/{session_id}/q-{question_id}/',
  '/projects/survey/{session_id}/q-{question_id}/next/',
  '/projects/survey/{session_id}/q-{question_id}/previous/',
  '/projects/survey/{session_id}/refresh',
  '/projects/survey/{session_id}/start/',
  '/projects/task-recommendation/{recommendation_id}/delete',
  '/projects/task-recommendation/{recommendation_id}/update',
  '/ressource/{pk}/revision/',
  '/ressource/{pk}/revision/{rev_pk}',
  '/ressource/{resource_id}/',
  '/ressource/{resource_id}/bookmark/create/',
  '/ressource/{resource_id}/bookmark/delete/',
  '/ressource/{resource_id}/delete',
  '/ressource/{resource_id}/embed',
  '/ressource/{resource_id}/update/',
  '/survey/editor/choice/{choice_id}/delete/',
  '/survey/editor/choice/{choice_id}/update/',
  '/survey/editor/question/{question_id}/choice/create/',
  '/survey/editor/question/{question_id}/delete/',
  '/survey/editor/question/{question_id}/results.csv',
  '/survey/editor/question/{question_id}/results/',
  '/survey/editor/question/{question_id}/update/',
  '/survey/editor/question_set/{question_set_id}/',
  '/survey/editor/question_set/{question_set_id}/delete/',
  '/survey/editor/question_set/{question_set_id}/question/create/',
  '/survey/editor/question_set/{question_set_id}/update/',
  '/survey/editor/survey/{survey_id}/',
  '/survey/editor/survey/{survey_id}/question_set/create/',
  '/task/followup/{followup_id}/edit/',
  '/task/rsvp/{rsvp_id}/{status}/',
  '/task/{task_id}/already/',
  '/task/{task_id}/delete/',
  '/task/{task_id}/followup/',
  '/task/{task_id}/refuse/',
  '/task/{task_id}/sort/{order}',
  '/task/{task_id}/toggle-done/',
  '/task/{task_id}/update/',
  '/task/{task_id}/visit/',
];
 */
