import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only overview page', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to the overview page and not see the advisor note', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.contains('Note interne').should('not.exist');
  });
});
