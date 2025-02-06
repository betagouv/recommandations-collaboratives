import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can see and update an advisor note', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to project overview and update advisor note', () => {
    cy.visit(`/project/${currentProject.pk}`);

    cy.contains('Note interne aux conseillers');

    cy.get('[data-cy="edit-internal-note"]').click({ force: true });

    const now = new Date();

    cy.get('textarea').clear({ force: true });

    cy.get('textarea')
      .type(`test : ${now}`)
      .should('have.value', `test : ${now}`);

    cy.contains('Enregistrer').click({ force: true });

    cy.contains(`test : ${now}`);
  });
});
