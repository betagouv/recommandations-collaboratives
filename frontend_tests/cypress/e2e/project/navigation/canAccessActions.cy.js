import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can access actions tab in a project as a member', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the action page of my project', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
  });
});

describe('I can access actions tab in a project as an advisor', () => {
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
