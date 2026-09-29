import projects from '../../../../fixtures/projects/projects.json';

const currentProject = projects[1]; // pk 2 - conseiller3 is NOT advisor of this project

describe('I can read only recommandations @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to the conversation and cannot create a recommendation', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-test-id="project-navigation-conversations-new"]').should(
      'have.attr',
      'disabled'
    );

    // Advisor on another territory only: the recommendation creation entry
    // point must not be available.
    cy.get('[data-test-id="create-task-button"]').should('not.exist');
  });
});
