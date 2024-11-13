import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only overview page', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to overview and read only content', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.url().should('include', '/presentation');

    cy.contains('Note interne').should('not.exist');
  });
});
