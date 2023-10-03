describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject(1)
    })

    it('publishes a task', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask(1);

        cy.get('[data-test-id="list-tasks-switch-button"]').should('have.class', 'active')
        cy.get('#unpublish-task-button').click({force:true});
        cy.get('[data-test-id="task-draft-status"]').should('be.visible')
        cy.get('#publish-task-button').click({force:true});
        cy.get('[data-test-id="task-draft-status"]').should('not.exist')
    })
})
