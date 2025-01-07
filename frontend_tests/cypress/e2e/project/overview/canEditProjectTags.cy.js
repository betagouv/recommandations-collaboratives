import projects from '../../../fixtures/projects/projects.json';

let currentProject = projects[9];

describe('I can edit project tags on overview page', () => {
  beforeEach(() => {
    cy.login('staff');
    cy.visit(`/project/1`);
  });

  it('adds new tags on project overview', () => {
    cy.get('[data-cy="overview-add-project-tag"]').click();
    cy.get('#id_tags').type('new-tag', { delay: 0 });
    cy.get('[data-cy="btn-submit-project-tag"]').click();
    cy.url().should('include', '/project/1/presentation');
    cy.get('[data-cy="container-tags"]').contains('new-tag');
    cy.get('[data-cy="overview-edit-project-tag"]').click();
    cy.get('#id_tags').clear();
    cy.get('[data-cy="btn-submit-project-tag"]').click();
    cy.url().should('include', '/project/1/presentation');
    cy.get('[data-cy="container-tags"]').should('not.exist');
  });
});
