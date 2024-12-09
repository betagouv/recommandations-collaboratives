import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can not comment a draft task', () => {

  it('as advisor I can see ', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk);
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.get('[data-test-id="see-suggest-task-button"]').click();
    cy.url().should('include', '/suggestions')
  });

    xit('as staff I can see ', () => {
        cy.login('staff');
        cy.visit(`/project/${currentProject.pk}`);
        cy.becomeAdvisor(currentProject.pk);
        cy.visit(`/project/${currentProject.pk}/actions`);
        cy.get('[data-test-id="see-suggest-task-button"]').click();
        cy.url().should('include', '/suggestions')
    });

    xit('as admin I can see ', () => {
        cy.login('admin');
        cy.visit(`/project/${currentProject.pk}`);
        cy.becomeAdvisor(currentProject.pk);
        cy.visit(`/project/${currentProject.pk}/actions`);
        cy.get('[data-test-id="see-suggest-task-button"]').click();
        cy.url().should('include', '/suggestions')
    });

    xit('as collectivité1 I can see ', () => {
        cy.login('collectivité1');
        cy.visit(`/project/${currentProject.pk}`);
        cy.becomeAdvisor(currentProject.pk);
        cy.visit(`/project/${currentProject.pk}/actions`);
        cy.get('[data-test-id="see-suggest-task-button"]').click();
        cy.url().should('include', '/suggestions')
    });
});

// page recommandations
