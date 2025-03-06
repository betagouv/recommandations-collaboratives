import projects from '../../../../fixtures/projects/projects.json';
import projectView from '../../../../support/views/project';

const currentProject = projects[17];

describe('As an advisor, I can quit a project', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
  });

  it('I can quit or join a project as observer or advisor', () => {
    cy.get('[data-test-id="header-banner-advising-position"]').click({
      force: true,
    });
    projectView.joinAsAdvisorWithSelector();
    projectView.joinAsObserverWithSelector();
    cy.get('[data-test-id="show-banner"]').click({ force: true });
    projectView.quitProjectRole();
    projectView.joinAsObserverWithSelector();
    projectView.joinAsAdvisorWithSelector();
    cy.get('[data-test-id="show-banner"]').click({ force: true });
    projectView.quitProjectRole();
  });
});
