import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';

const currentProject = projects[17];

describe('As project owner, I cannot quit a project @page-projet-parametres-quitter-projet', () => {
  beforeEach(() => {
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}`);
  });

  it(`I can't quit a project that I own`, () => {
    projectView.navigateToPreferencesTab();
    projectView.quitProject('owner');
  });
});
