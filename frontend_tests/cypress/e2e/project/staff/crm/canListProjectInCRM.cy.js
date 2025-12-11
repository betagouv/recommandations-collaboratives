import projects from '../../../../fixtures/projects/projects.json';
const projectCommune3Length = projects.filter(
  (project) => project.fields.commune === 3
).length;
describe('I can go to CRM and list projects', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/crm/project`);
  });

  xit('lists projects', () => {
    cy.contains(projects[0].fields.name).should('be.visible');
    cy.contains('random name').should('not.exist');
    cy.get('[data-test-id="projects-count-label"]').should(
      'contain.text',
      `${projects.length} résultat${projects.length > 1 ? 's' : ''}`
    );
  });

  xit('filters projects by name', () => {
    cy.get('[data-cy="search-bar-project"]').type(
      projects[projects.length - 1].fields.name
    );
    cy.contains(projects[projects.length - 1].fields.name).should('be.visible');
    cy.get('[data-test-id="projects-count-label"]').should(
      'contain.text',
      `1 résultat`
    );
    cy.get('[data-cy="search-bar-project"]')
      .clear()
      .type('random name with no results');
    cy.contains('Aucun résultat').should('be.visible');
    cy.get('[data-test-id="projects-count-label"]').should(
      'contain.text',
      `Aucun résultat`
    );
  });

  xit('filters projects department', () => {
    cy.get('#allTerritory').uncheck({ force: true });
    cy.wait(300);
    cy.get('#93').check({ force: true });
    cy.contains(
      projects.find((project) => project.fields.commune === 3).fields.name
    ).should('be.visible');
    cy.get('[data-test-id="projects-count-label"]').should(
      'contain.text',
      `${projectCommune3Length} résultats`
    );
  });
});
