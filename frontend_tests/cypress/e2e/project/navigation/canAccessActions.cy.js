import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

// TODO Réécrire pour la nouvelle interface conversation+panneau actions
//      (l'onglet "Recommandations" n'existe plus, /actions redirige vers /conversations#actions)
describe.skip('I can access actions tab in a project as a member', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the action page of my project', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
  });
});

describe.skip('I can access actions tab in a project as an advisor', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('goes to the action page of my project', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
  });
});

// page dossier
