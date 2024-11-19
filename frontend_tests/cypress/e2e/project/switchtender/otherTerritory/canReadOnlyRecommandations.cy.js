import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can read only recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to recommandations and read only content', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.contains('Ajouter une recommandation').should('not.exist');
  });
});
