let projectsLength;
describe('I can go to the dashboard and search for project', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit('/projects');
  });

  it('search project by name', () => {
    cy.get('[data-cy="loader"]').should('not.be.visible');
    cy.get('[data-cy="card-project"]')
      .its('length')
      .then((length) => {
        projectsLength = length;
        expect(projectsLength).to.be.greaterThan(0);
        cy.get('[data-cy="search-bar-project"]').type('map area commune', {
          delay: 0,
        });
        cy.get('[data-cy="card-project"]')
          .its('length')
          .should('be.lessThan', projectsLength);
        cy.contains('Map Area Commune');
      });
  });

  it('does not display pre-draft projects on kanban', () => {
    cy.get('[data-cy="loader"]').should('not.be.visible');
    cy.get('[data-cy="card-project"]')
      .its('length')
      .then((length) => {
        projectsLength = length;
        expect(projectsLength).to.be.greaterThan(0);
        cy.get('[data-cy="search-bar-project"]').type('pre-draft', {
          delay: 0,
        });
        cy.contains('Dossier pre-draft').should('not.exist');
      });
  });

  it('could not display unknown project', () => {
    cy.get('[data-cy="loader"]').should('not.be.visible');
    cy.get('[data-cy="card-project"]')
      .its('length')
      .then((length) => {
        projectsLength = length;
        expect(projectsLength).to.be.greaterThan(0);
        cy.get('[data-cy="search-bar-project"]').type("n'importe qoi", {
          delay: 0,
        });
        cy.get('[data-cy="card-project"]').should('not.exist');
      });
  });

  it('could search by territory', () => {
    cy.get('[data-cy="loader"]').should('not.be.visible');
    cy.get('[data-cy="card-project"]')
      .its('length')
      .then((length) => {
        projectsLength = length;
        expect(projectsLength).to.be.greaterThan(0);

        cy.get('[data-cy="check-display-project"]').click();
        cy.get('#region-1').should('be.visible');
        cy.get('#region-1').should('be.checked');
        cy.get('#region-1').uncheck();
        cy.contains('93170').should('not.exist');
      });
  });
});
