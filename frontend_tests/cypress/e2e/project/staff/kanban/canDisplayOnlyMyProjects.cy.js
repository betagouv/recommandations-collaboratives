let projectsLength;
//TODO: Verify when the fixing frontend test environment is done
describe('I can go to the dashboard and see only my projects', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.visit('/projects/staff/');
  });

  it('search project by name', () => {
    projectsLength = cy.get('[data-cy="card-project"]').length;
    cy.get('[data-test-id="my-projects-toggle"]').should('be.visible');
    cy.get('[data-test-id="my-projects-toggle"]').should('be.unchecked');
    cy.get('[data-test-id="my-projects-toggle"]').check();
    cy.get('[data-cy="card-project"]').should(
      'have.length.lowerThan',
      projectsLength
    );
  });
});
