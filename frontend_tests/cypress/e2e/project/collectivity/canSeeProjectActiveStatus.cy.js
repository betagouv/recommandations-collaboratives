import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';

const currentProject = projects[21];

describe(`As non referent project member, I can see a project's active status`, () => {
  before(() => {
    // First: login as owner and deactivate project
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/administration`);
    projectView.deactivateProject();
    cy.logout();
  });

  it('Displays a header banner when a project is paused', () => {
    // Then: login as non referent project member and check banner
    cy.login('collectivité2');
    cy.visit(`/project/${currentProject.pk}/administration`);
    projectView.navigateToPreferencesTab();
    projectView.checkProjectStatusBanner('exist');
  });
});
