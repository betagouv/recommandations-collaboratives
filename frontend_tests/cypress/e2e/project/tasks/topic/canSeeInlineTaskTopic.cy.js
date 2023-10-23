describe('I can go to tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject('test project')
        cy.becomeAdvisor();
    })

    it('sees a task inline topic', () => {

        cy.becomeAdvisor();
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask('inline task','inline topic');

        cy.get('[data-test-id="list-tasks-switch-button"]').should('have.class', 'active')
        cy.get('[data-test-id="task-inline-topic"]').should('exist')
    })
})
