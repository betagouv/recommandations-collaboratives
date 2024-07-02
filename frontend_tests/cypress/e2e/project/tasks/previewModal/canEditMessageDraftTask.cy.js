import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can not comment a draft task', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.declineCookies();
  });

  it('opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask('test');

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

    cy.get('[data-test-id="open-task-actions-button"]')
      .first()
      .click({ force: true });
    cy.contains('Modifier').click({ force: true });

    cy.get('#intent')
      .type(` edited`, { force: true })
      .should('have.value', `Draft reco edited`);

    cy.get('textarea')
      .type(` new value`, { force: true })
      .should('have.value', `reco test from action description new value`);

    cy.get('[data-test-id="publish-draft-task-button"]')
      .trigger('click')
      .click();
    cy.url().should('include', '/actions');

    cy.contains('Draft reco edited').click({ force: true });
    cy.contains('reco test from action description new value');

    // cy.get('[data-test-id="button-submit-new"]').should('not.exist');
  });
});
