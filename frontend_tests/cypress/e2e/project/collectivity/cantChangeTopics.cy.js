import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe("I can't change topics of a project", () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to overview page and should not see edit topic button', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.url().should('include', '/presentation');

    cy.contains('Identifier les sujets').should('not.exist');
  });
});
