import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe('As an advisor, I can quit a project @page-projet-parametres-quitter-projet', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
  });

  it('I can quit or join a project as observer or advisor', () => {
    projectView.joinAsAdvisorWithSelector();
    cy.get('[data-test-id="button-quit-role"]').should('exist');
    projectView.quitProjectRole();
  });
});
