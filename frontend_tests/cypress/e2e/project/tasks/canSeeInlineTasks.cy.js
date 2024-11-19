let currentProjectId;
describe('I can go to tasks tab', () => {
  before(() => {
    cy.login('conseiller1');
    cy.createProject('Count Published Project').then((projectId) => {
      currentProjectId = projectId;
      cy.visit('/projects/advisor');
      cy.get('[data-test-id="project-link"]').first().click();
      cy.becomeAdvisor(currentProjectId);
      cy.visit(`/project/${currentProjectId}/actions`);
      cy.createTask('published task');
      cy.createTask('drafted task', 'drafted label', false, true);
    });
  });

  it('list all inline tasks, count task and ignore drafted one', () => {
    cy.visit(`/project/${currentProjectId}/actions`);
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
    cy.get('[data-test-id="tasks-count"]').should(
      'have.text',
      '1 recommandation'
    );
  });
});
