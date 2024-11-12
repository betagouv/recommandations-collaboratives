import documents from '../../../fixtures/documents/documents.json';
import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can unbookmark a file already pinned', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('shows the unpinned file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    //Unbookmark a file
    cy.contains(documents[2].fields.description)
      .parent()
      .parent()
      .parent()
      .find('#file-is-not-bookmarked');
    cy.contains(documents[2].fields.description)
      .parent()
      .parent()
      .parent()
      .find('#file-is-not-bookmarked')
      .click({ force: true });
  });

  it('checks if the file is now correctly bookmarked', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(documents[2].fields.description)
      .parent()
      .parent()
      .parent()
      .find('#file-is-bookmarked');
  });
});
