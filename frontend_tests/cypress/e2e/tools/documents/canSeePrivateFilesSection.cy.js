import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('Private files section visibility on documents page', () => {
  it('advisor can see the private files section', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/documents`);
    cy.get('[data-test-id="private-files-section"]').should('exist');
  });

  it('collectivité cannot see the private files section', () => {
    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/documents`);
    cy.get('[data-test-id="private-files-section"]').should('not.exist');
  });
});
