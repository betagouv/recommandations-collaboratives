let projectsLength;
//TODO: Verify when the fixing frontend test environment is done
describe('I can go to the dashboard and see only my projects', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.visit('/projects/staff/');
  });

  it('search project by name', () => {
    cy.get('[data-cy="card-project"]').then(($projects) => {
      const visibleProjects = $projects.filter((_, project) => {
        return Cypress.$(project).css('display') !== 'none';
      });
      projectsLength = visibleProjects.length;
      cy.log(`Nombre initial de dossiers: ${projectsLength}`);
    });

    cy.get('[data-test-id="my-projects-toggle"]').should('be.not.checked');
    cy.get('[data-test-id="my-projects-toggle"]').check();
    cy.get('[data-cy="card-project"]').should(($projects) => {
      const visibleProjects = $projects.filter((_, project) => {
        return Cypress.$(project).css('display') !== 'none';
      });
      expect(visibleProjects.length).to.be.lessThan(projectsLength);
    });
  });
});
