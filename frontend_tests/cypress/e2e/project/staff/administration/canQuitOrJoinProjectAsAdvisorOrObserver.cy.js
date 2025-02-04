import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe('As an advisor, I can quit a project', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${currentProject.pk}`);
  });

  it('I can quit or join a project as observer or advisor', () => {
    projectView.joinAsObserverWithSelector();
    cy.get('[data-test-id="show-banner"]').click({ force: true });
    projectView.quitProjectRole();
    projectView.joinAsAdvisorWithSelector();
    cy.get('[data-test-id="show-banner"]').click({ force: true });
    cy.get('[data-test-id="button-quit-role"]').should('exist');
  });
});
