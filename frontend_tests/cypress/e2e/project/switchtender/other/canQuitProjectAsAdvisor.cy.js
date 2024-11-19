import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe('As an advisor, I can quit a project', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
  });

  it('I can quit a project from the project preferences', () => {
    projectView.joinAsObserver();
    projectView.navigateToPreferencesTab();
    projectView.quitProject('advisor');
  });
});
