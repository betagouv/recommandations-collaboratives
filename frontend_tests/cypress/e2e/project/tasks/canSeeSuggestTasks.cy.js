import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can see suggest task', () => {
  it('as advisor I can see ', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du dossier
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('[data-test-id="see-suggest-task-button"]').click();
    cy.url().should('include', '/suggestions');
  });

  it('as staff I can see ', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du dossier
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('[data-test-id="see-suggest-task-button"]').click();
    cy.url().should('include', '/suggestions');
  });
});

// page recommandations
