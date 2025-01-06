import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can not comment a draft task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('should create task and opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.get('[data-test-id="create-task-button"]').click({ force: true });

    cy.get('#push-noresource').click({ force: true });

    cy.get('#intent')
      .type(`Draft reco`, { force: true, delay: 0 })
      .should('have.value', `Draft reco`);

    cy.get('textarea')
      .type(`reco test from action description`, { force: true, delay: 0 })
      .should('have.value', `reco test from action description`);

    cy.get('[data-test-id="publish-draft-task-button"]')
      .trigger('click')
      .click();

    cy.url().should('include', '/actions');

    cy.contains('Draft reco').click({ force: true });

    cy.get('[data-test-id="button-submit-new"]').should('not.exist');
  });
});

// page recommandation
