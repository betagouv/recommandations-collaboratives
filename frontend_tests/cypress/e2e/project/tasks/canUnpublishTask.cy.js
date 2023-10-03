describe('I can go tasks tab', () => {
    beforeEach(() => {
        cy.login("jean");
        cy.createProject("unpublish task")
    })

    it('unpublishes a task', () => {

        cy.becomeAdvisor();

        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

        cy.createTask("unpublish task");

        cy.get('[data-test-id="list-tasks-switch-button"]').should('have.class', 'active')

        cy.get('#unpublish-task-button').click({force:true});

        cy.contains('brouillon')
    })
})
