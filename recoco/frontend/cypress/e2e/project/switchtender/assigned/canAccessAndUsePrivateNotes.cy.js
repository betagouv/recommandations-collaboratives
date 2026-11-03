import projects from '../../../../fixtures/projects/projects.json';
import editor from '../../../../support/tools/editor';

const currentProject = projects[1];

describe('I can access and use private notes @page-projet-espace-conseiller @page-projet-espace-conseiller-nouveau-message', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to private notes', () => {
    cy.visit(`/project/${currentProject.pk}/suivi`);

    const now = new Date();

    cy.get('textarea')
      .type(`test : ${now}`, { force: true })
      .should('have.value', `test : ${now}`);

    editor.writeMessage(`test : ${now}`);

    cy.contains('Enregistrer').click({ force: true });

    cy.contains(`test : ${now}`);
  });
});
