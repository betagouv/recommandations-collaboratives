import file from '../../../fixtures/documents/file.json';
import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can add a file on the document tab', () => {
  before(() => {
    cy.login('collectivité1');
  });

  it('upload a file', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.document().then((doc) => {
      var popover = doc.getElementById('popover');
      popover.style = 'display:block !important;';

      cy.get('[name="the_file"]').selectFile(file.path, { force: true });
      cy.get('#document-description')
        .type(file.description, { force: true, delay: 0 })
        .should('have.value', file.description);
      cy.get('#document-submit-button').click({ force: true });
    });

    cy.contains('Le document a bien été enregistré');
  });

  it('show the file in the file list', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(file.description);
  });
});
