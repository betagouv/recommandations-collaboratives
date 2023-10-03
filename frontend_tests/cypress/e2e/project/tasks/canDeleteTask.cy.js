describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject('delete task')
    })

    it('deletes a task', () => {

        cy.becomeAdvisor();
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask('test');

        cy.get('[data-test-id="list-tasks-switch-button"]').should('have.class', 'active')
        cy.get('[data-test-id="delete-task-action-button"]').click({force:true});
        cy.get('[data-test-id="delete-task-modal-button"]').click({force:true});
        cy.get('[data-test-id="no-tasks-banner"]').should('exist')
    })
})
