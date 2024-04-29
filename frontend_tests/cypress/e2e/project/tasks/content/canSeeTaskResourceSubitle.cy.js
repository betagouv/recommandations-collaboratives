import resources from '../../../../fixtures/resources/resources.json';
const currentResource = resources[4];
const taskName = 'task intent';

describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login('jean');
        cy.createProject('task intent');
    });

    it('creates a task with a resource and see the resource subtitle', () => {
        cy.visit(`/projects`);
        cy.contains('commune de test').click({ force: true });
        cy.becomeAdvisor();
        // cy.get('[id="project-67"]').click({ force: true });
        cy.contains('Recommandations').click({ force: true });
        cy.url().should('include', '/actions');

        cy.createTask(taskName, '', true);
        cy.get('[data-test-id="list-tasks-switch-button"]').should(
            'have.class',
            'active'
        );

        cy.contains(currentResource.fields.subtitle);
    });
});
