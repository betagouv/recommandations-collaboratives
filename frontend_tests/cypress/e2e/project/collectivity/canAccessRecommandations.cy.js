import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can access the recommandations', () => {
  before(() => {
    cy.login('jean');
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.createTask('Notif test');
    cy.logout();
  });

  beforeEach(() => {
    cy.login('bob');
  });

  it('goes to recommandations tab and see new recommandations', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });

    cy.url().should('include', '/actions');

    cy.get('Ajouter une recommandation').should('not.exist');

    cy.get('[data-test-id="badge-new-task"]')
      .should('exist')
      .first()
      .click({ force: true });
    cy.wait(500);
    cy.get('[data-test-id="close-modal-task"]').click({ force: true });
    cy.get('[data-test-id="banner-new-tasks"]').should('not.exist');
    cy.get('[data-test-id="badge-new-task"]').should('not.be.visible');
  });
});
