import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only project state', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to project state and read only content', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.get('[data-test-id="project-navigation-knowledge"]').click();

    cy.url().should('include', '/connaissance');

    cy.contains('Compléter cette section').should('not.exist');
  });
});
