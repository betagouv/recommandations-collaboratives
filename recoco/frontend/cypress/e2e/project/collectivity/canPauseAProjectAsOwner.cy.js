import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';

const currentProject = projects[17];

describe('As project owner, I can pause a project @page-projet-parametres-pause-projet', () => {
  beforeEach(() => {
    cy.login('collectivité1');
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
