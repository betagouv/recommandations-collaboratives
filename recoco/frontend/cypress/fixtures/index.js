const fixtures = [
  // Site configuration
  './cypress/fixtures/settings/siteWithOnboardingAndSurvey.json',

  // Settings
  './cypress/fixtures/settings/featureFlags.json',

  // Users
  './cypress/fixtures/users/users.json',
  './cypress/fixtures/users/accountEmailAddress.json',

  // Geography
  './cypress/fixtures/geomatics/region.json',
  './cypress/fixtures/geomatics/department.json',
  './cypress/fixtures/geomatics/commune.json',

  // Projects
  './cypress/fixtures/projects/projects.json',
  './cypress/fixtures/projects/projectsSites.json',
  './cypress/fixtures/projects/projectsMembers.json',
  './cypress/fixtures/projects/reminders.json',

  // Addressbook, profiles, resources and documents
  './cypress/fixtures/addressbook/organizations.json',
  './cypress/fixtures/profiles/profiles.json',
  './cypress/fixtures/resources/resources.json',
  './cypress/fixtures/addressbook/contacts.json',
  './cypress/fixtures/documents/documents.json',

  './cypress/fixtures/settings/challengeDefinition.json',
  './cypress/fixtures/projects/tasks.json',
  './cypress/fixtures/conversations/conversations.json',
  './cypress/fixtures/users/advisorAccessRequest.json',
  './cypress/fixtures/projects/invites.json',
  './cypress/fixtures/settings/tag.json',
];

console.log(fixtures.join(' '));
