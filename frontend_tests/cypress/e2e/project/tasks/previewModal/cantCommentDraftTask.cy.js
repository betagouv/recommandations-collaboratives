import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can not comment a draft task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('should create task and opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    cy.get('[data-test-id="create-task-button"]').click({ force: true });

    cy.get('#push-noresource').click({ force: true });

    cy.get('#intent')
      .type(`Draft reco`, { force: true })
      .should('have.value', `Draft reco`);

    cy.get('textarea')
      .type(`reco test from action description`, { force: true })
      .should('have.value', `reco test from action description`);

    cy.get('[data-test-id="publish-draft-task-button"]')
      .trigger('click')
      .click();

    cy.url().should('include', '/actions');

    cy.contains('Draft reco').click({ force: true });

    cy.get('[data-test-id="button-submit-new"]').should('not.exist');
  });
});
