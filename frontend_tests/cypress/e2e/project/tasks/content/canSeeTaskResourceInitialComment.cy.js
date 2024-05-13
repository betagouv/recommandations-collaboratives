// import resources from '../../../../fixtures/resources/resources.json'

// const currentResource = resources[4]
const taskName = 'task intent';

describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login('jean');
        cy.createProject('new task');
    });

    it('creates a task with a resource and see the initial comment', () => {
        cy.visit(`/projects`);
        cy.contains('new task').first().click({ force: true });
        cy.becomeAdvisor();
        // cy.wait(1000);
        // cy.get('[data-test-id]="button-join-as-advisor"').click({
        //     force: true,
        // });
        // cy.contains('Conseiller le projet').click({ force: true });
        cy.contains('Recommandations').click({ force: true });
        cy.url().should('include', '/actions');

        cy.createTask(taskName, '', true);
        cy.get('[data-test-id="list-tasks-switch-button"]').should(
            'have.class',
            'active'
        );

        cy.get('[data-test-id="task-initial-comment"]').should('exist');
    });
});
