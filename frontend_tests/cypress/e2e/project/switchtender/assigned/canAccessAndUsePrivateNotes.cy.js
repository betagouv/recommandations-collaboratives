import projects from '../../../../fixtures/projects/projects.json';
import editor from '../../../../support/tools/editor';

const currentProject = projects[1];

describe('I can access and use private notes', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to private notes', () => {
    cy.visit('/projects');

    cy.contains(currentProject.fields.name).click({ force: true });

    cy.contains('Espace conseiller').click({ force: true });

    cy.url().should('include', '/suivi');

    const now = new Date();

    cy.get('textarea')
      .type(`test : ${now}`, { force: true })
      .should('have.value', `test : ${now}`);

    editor.writeMessage(`test : ${now}`);

    cy.contains('Envoyer').click({ force: true });

    cy.contains(`test : ${now}`);
  });
});
