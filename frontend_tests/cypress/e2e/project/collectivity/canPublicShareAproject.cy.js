import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[2];

describe('I can have a public url to share', () => {
  it('goes to share a project page', () => {
    cy.login('collectivité2');
    cy.visit(`/project/${currentProject.pk}/connaissance`);

    cy.get('[data-test-id="public-share-button"]').click({ force: true });

    // cy.url().should('include', '/access/')

    cy.document().then((doc) => {
      const value = doc.querySelector('[x-ref="input"]').value;
      cy.visit(value);
      cy.url().should('include', '/project/partage/');
    });
  });
});
