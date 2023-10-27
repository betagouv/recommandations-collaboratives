describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject('test project 2')
        cy.becomeAdvisor();
    })

    it('sees a task kanban topic', () => {

        cy.becomeAdvisor();
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask('inline task','kanban topic');

        cy.get('[data-test-id="kanban-tasks-switch-button"]').click({ force: true })
        cy.get('[data-test-id="kanban-tasks-switch-button"]').should('have.class', 'active')
        cy.get('[data-test-id="task-kanban-topic"]').should('exist')
    })
})
