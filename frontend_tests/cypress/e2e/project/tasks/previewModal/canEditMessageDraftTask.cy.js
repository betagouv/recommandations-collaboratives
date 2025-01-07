import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can not comment a draft task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du projet
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.createTask('test');

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

    cy.get('[data-test-id="open-task-actions-button"]')
      .first()
      .click({ force: true });
    cy.contains('Modifier').click({ force: true });

    cy.get('#intent')
      .type(` edited`, { force: true, delay: 0 })
      .should('have.value', `Draft reco edited`);

    cy.get('textarea')
      .type(` new value`, { force: true, delay: 0 })
      .should('have.value', `reco test from action description new value`);

    cy.get('[data-test-id="publish-draft-task-button"]')
      .trigger('click')
      .click();
    cy.url().should('include', '/actions');

    cy.contains('Draft reco edited').click({ force: true });
    cy.contains('reco test from action description new value');
  });
});

// page recommandation
