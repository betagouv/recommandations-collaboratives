import link from '../../../fixtures/documents/link.json';
import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can add a link on the document tab', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('add a link', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.document().then((doc) => {
      var popover = doc.getElementById('link-popover');
      popover.style = 'display:block !important;';

      cy.get('[name="the_link"]')
        .type(link.url, { force: true, delay: 0 })
        .should('have.value', link.url);
      cy.get('#link-description')
        .type(link.description, { force: true, delay: 0 })
        .should('have.value', link.description);
      cy.get('#link-submit-button').click({ force: true });
    });
  });

  it('show the link in the link list', () => {
    cy.visit(`/project/${currentProject.pk}/documents`);

    cy.contains(link.description);
  });
});
