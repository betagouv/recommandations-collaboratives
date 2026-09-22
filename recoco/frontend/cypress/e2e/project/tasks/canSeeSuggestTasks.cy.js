import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1]; // pk 2 - conseiller1 advisor

describe('I can see suggest task @page-projet-recommandations', () => {
  it('as advisor I can access the suggested resources page', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/suggestions/`);
    cy.url().should('include', '/suggestions');
  });

  it('as staff I can access the suggested resources page', () => {
    cy.login('staff');
    cy.visit(`/project/${currentProject.pk}/suggestions/`);
    cy.url().should('include', '/suggestions');
  });
});
