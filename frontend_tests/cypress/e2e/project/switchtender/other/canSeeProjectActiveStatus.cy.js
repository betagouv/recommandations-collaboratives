import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe(`As project advisor, I can see a project's active status`, () => {
  before(() => {
    // First: login as owner and deactivate project
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${currentProject.pk}`);

    projectView.navigateToPreferencesTab();
    projectView.deactivateProject();
    cy.logout();
  });

  it('Displays a header banner when a project is paused', () => {
    // Then: login as non referent project member and check banner
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    projectView.checkProjectStatusBanner('exist');
  });
});
