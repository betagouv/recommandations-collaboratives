import documents from '../../../fixtures/documents/documents.json';
import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can delete a file on the document tab', () => {
  before(() => {
    cy.login('collectivité1');
  });

  it('deletes a file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(documents[3].fields.description)
      .parent()
      .parent()
      .parent()
      .find('#file-delete-button')
      .click({ force: true });

    cy.contains('Le document a bien été supprimé');
  });

  it('must not show the deleted link', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(documents[3].fields.description).should('not.exist');
  });
});
