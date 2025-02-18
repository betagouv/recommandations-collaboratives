import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe('As site staff, I can quit a project', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${currentProject.pk}`);
    projectView.joinAsAdvisorWithSelector();
  });

  it('I can quit a project from the project preferences', () => {
    projectView.navigateToPreferencesTab();
    projectView.quitProject('staff');
  });
});
