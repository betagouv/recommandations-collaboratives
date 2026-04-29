import projects from '../../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe.skip('I can read only recommandations @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller2');
  });

  it('goes to recommandations and read only content', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.contains('Ajouter une recommandation').should('not.exist');
  });
});

// page recommandations
