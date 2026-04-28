import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

// TODO Réécrire pour la nouvelle interface conversation (/actions redirige vers /conversations#actions)
describe.skip('I can read only recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to recommandations and read only content', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.contains('Ajouter une recommandation').should('not.exist');
  });
});

// page recommandations
