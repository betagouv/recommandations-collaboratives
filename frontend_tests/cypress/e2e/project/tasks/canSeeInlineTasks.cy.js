describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.createProject('Count Published Project');
  });

  it('list all inline tasks', () => {
    cy.visit('/projects/advisor').then(() => {
      cy.get('[data-test-id="project-link"]').first().click();
      cy.becomeAdvisor();
      cy.contains('Recommandations').click({ force: true });
      cy.url().should('include', '/actions');
      cy.createTask('published task');
      cy.get('[data-test-id="list-tasks-switch-button"]').should(
        'have.class',
        'active'
      );
    });
  });

  it('count the number of published inline tasks', () => {
    cy.visit(`/projects`);
    cy.get('[data-test-id="project-link"]').first().click();
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask('published task');
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.get('[data-test-id="tasks-count"]').should(
      'have.text',
      '1 recommandation'
    );
  });

  it('count the number of drafted inline tasks', () => {
    cy.visit(`/projects`);
    cy.get('[data-test-id="project-link"]').first().click();
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask('drafted task', 'drafted label', false, true);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.get('[data-test-id="tasks-count"]').should(
      'have.text',
      '0 recommandation'
    );
  });
});
