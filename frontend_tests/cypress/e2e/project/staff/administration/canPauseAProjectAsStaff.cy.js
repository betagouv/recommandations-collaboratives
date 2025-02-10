import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[19];

describe('As site staffOnSite, I can pause and reactivate a project', () => {
  beforeEach(() => {
    cy.login('staffOnSite');
    cy.visit(`/project/${currentProject.pk}`);
  });

  it('Pauses a project from the project preferences', () => {
    projectView.navigateToPreferencesTab();
    projectView.deactivateProject();
  });

  it('Reactivates a project from the project preferences', () => {
    projectView.navigateToPreferencesTab();
    projectView.activateProjectFromPreferences();
  });
});
