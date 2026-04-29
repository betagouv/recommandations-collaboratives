import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can access documents tab in a project @navigation-projet @page-projet-fichier', () => {
  it('goes to the documents page of my project as a member', () => {
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="project-navigation-documents"]').click({
      force: true,
    });
    cy.url().should('include', '/documents');
  });

  it('goes to the documents page of my project as an advisor', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    cy.get('[data-test-id="project-navigation-documents"]').click({
      force: true,
    });
    cy.url().should('include', '/documents');
  });
});
