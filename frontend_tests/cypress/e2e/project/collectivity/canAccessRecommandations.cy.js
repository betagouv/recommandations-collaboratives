import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can access the recommandations', () => {
  it('goes to recommandations tab and see new recommandations', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.createTask('Notif test');
    cy.logout();

    cy.login('collectivité1');
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('Ajouter une recommandation').should('not.exist');

    // TODO : using intercept and dynamic wait
    // cy.intercept(
    //   'POST',
    //   /\/api\/projects\/\d+\/tasks\/\d+\/notifications\/mark_all_as_read\/$/,
    //   'success'
    // ).as('markVisited');

    cy.get('[data-test-id="badge-new-task"]')
      .should('exist')
      .first()
      .click({ force: true });
    // TODO : using intercept and dynamic wait
    // cy.wait('@markVisited');
    cy.wait(500);
    cy.get('[data-test-id="close-modal-task"]')
      .should('exist')
      .click({ force: true });
    cy.get('[data-test-id="banner-new-tasks"]').should('not.exist');
    cy.get('[data-test-id="badge-new-task"]').should('not.be.visible');
  });
});
