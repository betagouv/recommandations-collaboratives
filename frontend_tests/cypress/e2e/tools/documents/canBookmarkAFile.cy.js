import documents from '../../../fixtures/documents/documents.json';
import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can bookmark and unbookmark a file', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('boomark a file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(documents[2].fields.description)
      .parent()
      .parent()
      .find('#file-is-not-bookmarked')
      .click();
    cy.contains(documents[2].fields.description)
      .parent()
      .parent()
      .find('#file-is-bookmarked');
  });

  it('unboomark a file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(documents[1].fields.description)
      .parent()
      .parent()
      .find('#file-is-bookmarked')
      .click();

    cy.contains(documents[1].fields.description)
      .parent()
      .parent()
      .find('#file-is-not-bookmarked');
  });
});
