import projectView from '../../../support/views/project';

describe('I can go to a project and select my role on it', () => {

  it('can become observer, advisor or quit project as regional advisor', () => {
    cy.login('jean');
    cy.visit('/project/2');
    projectView.quitProjectRole();
    //test to open role selector via banner
    cy.get('[data-test-id="join-project-banner"]').click({ force: true });
    cy.get('[data-test-id="selector-join-as-advisor"]').click({ force: true });
    cy.get('[data-test-id="button-validate-role"]').click({ force: true });
    projectView.quitProjectRole();
    projectView.joinAsObserverWithSelector();
    cy.get('[data-test-id="selector-join-as-observer"]').should('be.checked');

  });
});
